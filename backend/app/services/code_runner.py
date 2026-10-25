"""Hardened Python practice runner.

Untrusted learner code is executed only in a short-lived child process with
strict resource limits and a deliberately tiny import/builtin surface. This
module is for practice grading only; it must never be used for arbitrary
server jobs.
"""

from __future__ import annotations

import ast
import os
import secrets
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

MAX_CODE_BYTES = 64 * 1024
TIMEOUT_SECONDS = 3
MEMORY_BYTES = 256 * 1024 * 1024
MAX_OUTPUT_BYTES = 32 * 1024

FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "socket", "requests", "urllib", "http", "ftplib",
    "shutil", "pathlib", "glob", "tempfile", "ctypes", "multiprocessing", "threading",
    "asyncio", "signal", "resource", "importlib", "pickle", "marshal", "shelve",
    "sqlite3", "ssl", "webbrowser", "antigravity",
}
FORBIDDEN_NAMES = {
    "eval", "exec", "compile", "open", "input", "breakpoint", "help", "__import__",
    "globals", "locals", "vars", "dir", "getattr", "setattr", "delattr", "memoryview",
}

SAFE_BUILTINS = {
    "abs", "all", "any", "ascii", "bin", "bool", "bytes", "callable", "chr",
    "classmethod", "complex", "dict", "divmod", "enumerate", "filter", "float",
    "format", "frozenset", "hash", "hex", "int", "isinstance", "issubclass",
    "iter", "len", "list", "map", "max", "min", "next", "object", "oct", "ord",
    "pow", "print", "property", "range", "repr", "reversed", "round", "set",
    "slice", "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", "zip",
    # Exceptions are data, not capabilities: exercises need them to teach
    # validation, try/except, and defensive code.
    "AssertionError", "AttributeError", "ArithmeticError", "Exception",
    "FileNotFoundError", "IndexError", "KeyError", "NameError",
    "NotImplementedError", "OSError", "RuntimeError", "StopIteration",
    "TypeError", "ValueError", "ZeroDivisionError",
    # Required by Python's `class` statement inside exec().
    "__build_class__",
}

# Modules learner code may import. `sqlite3` is intentionally test-only: it can
# open database files, so exposing it to submissions would widen filesystem
# access beyond what a practice exercise needs.
LEARNER_MODULES = {
    "math", "random", "json", "re", "datetime", "collections", "itertools",
    "functools", "statistics", "string", "textwrap", "csv", "io",
    "dataclasses", "enum", "typing", "decimal", "fractions",
}

# Authored test code may use sqlite3 to build an in-memory database. Tests are
# never written by learners; the learner namespace still cannot import it.
TEST_MODULES = LEARNER_MODULES | {"sqlite3"}

# Attributes that would turn a harmless module into filesystem access.
FORBIDDEN_ATTRIBUTES = {"open", "FileIO", "connect", "executescript"}


class UnsafeCode(ValueError):
    pass


def _validate_ast(code: str, allowed_modules: set[str] | None = None, strict: bool = True) -> None:
    allowed = allowed_modules or LEARNER_MODULES
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise UnsafeCode(f"SyntaxError: {exc.msg} (line {exc.lineno})") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported = [node.module or ""]
        else:
            imported = []
        if imported:
            for name in imported:
                module = name.split(".")[0]
                if not module or module not in allowed:
                    raise UnsafeCode(f"Import '{module}' is not allowed in the practice sandbox.")
            continue
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_NAMES:
                raise UnsafeCode(f"'{node.func.id}' is not allowed in the practice sandbox.")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise UnsafeCode(f"'{node.id}' is not allowed in the practice sandbox.")
        elif strict and isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
            raise UnsafeCode(f"'{node.attr}' is not allowed in the practice sandbox.")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise UnsafeCode("Dunder attribute access is not allowed in the practice sandbox.")
        elif isinstance(node, ast.Name) and node.id.startswith("__"):
            raise UnsafeCode("Dunder names are not allowed in the practice sandbox.")


def _preexec_limits() -> None:
    # Render runs Linux. Keep imports local so the application can still be
    # imported on platforms where resource is unavailable (e.g. some dev OSes).
    import resource

    os.setsid()
    resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_SECONDS, TIMEOUT_SECONDS + 1))
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 * 1024 * 1024, 1 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    if hasattr(resource, "RLIMIT_NPROC"):
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))


def _runner_source(user_code: str, test_code: str, run_token: str) -> str:
    # The child receives a safe builtin allowlist and a restricted importer.
    # Tests run after learner code in the same namespace, but are never allowed
    # to expand the sandbox capabilities. There is no network, no os access,
    # no filesystem writes, and the process has CPU/memory/file-size limits.
    module_imports = "\n".join(f"import {name}" for name in sorted(TEST_MODULES))
    learner_map = ", ".join(f'"{name}": {name}' for name in sorted(LEARNER_MODULES))
    test_map = ", ".join(f'"{name}": {name}' for name in sorted(TEST_MODULES))
    template = r'''import builtins
import ast
import sys
__IMPORTS__

_SAFE = __SAFE__
_RUN_TOKEN = __RUN_TOKEN__
_OUTPUT_LIMIT = __OUTPUT_LIMIT__
_OUTPUT_FD = sys.stdout


class _LimitedOutput:
    """Swallow learner output past the limit instead of buffering it."""

    def __init__(self, stream, limit):
        self._stream = stream
        self._limit = limit
        self._written = 0

    def write(self, data):
        if not isinstance(data, str):
            data = str(data)
        remaining = self._limit - self._written
        if remaining > 0:
            self._stream.write(data[:remaining])
            self._written += min(len(data), remaining)
        return len(data)

    def flush(self):
        self._stream.flush()


_LIMITED = _LimitedOutput(_OUTPUT_FD, _OUTPUT_LIMIT)
sys.stdout = _LIMITED
_LEARNER_MODULES = {__LEARNER_MAP__}
_TEST_MODULES = {__TEST_MAP__}


def _make_importer(allowed):
    def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".")[0]
        if root not in allowed:
            raise ImportError(f"Import '{name}' is not allowed in the practice sandbox.")
        return allowed[root]
    return _safe_import


_SAFE_BUILTINS = {name: getattr(builtins, name) for name in _SAFE}
_SAFE_BUILTINS["__import__"] = _make_importer(_LEARNER_MODULES)
_TEST_BUILTINS = dict(_SAFE_BUILTINS)
_TEST_BUILTINS["__import__"] = _make_importer(_TEST_MODULES)

_NS = {"__builtins__": _SAFE_BUILTINS, "__name__": "__dsir__"}

# Learner code
exec(compile(__USER_CODE__, "<learner>", "exec"), _NS, _NS)

# Test setup and assertions run in a trusted namespace that can see learner
# definitions but does not widen the learner's capabilities.
_TEST_NS = dict(_NS)
_TEST_NS["__builtins__"] = _TEST_BUILTINS

_TEST_CODE = __TEST_CODE__
_TEST_TREE = ast.parse(_TEST_CODE)
_TEST_LINES = _TEST_CODE.splitlines()


def _segment(node):
    return "\n".join(_TEST_LINES[node.lineno - 1:node.end_lineno])


_test_nodes = []
for _node in _TEST_TREE.body:
    if isinstance(_node, (ast.Assert, ast.Try)):
        _test_nodes.append(_node)
    else:
        exec(compile(_segment(_node), "<tests>", "exec"), _TEST_NS, _TEST_NS)

# Protocol lines go to stderr. Learner code cannot reach stderr, so stdout
# flooding cannot truncate the result and stdout cannot forge it.
if not _test_nodes:
    print(f"__DSIR_RESULT__:{_RUN_TOKEN}:1:1:0", file=sys.stderr)
else:
    _passed = 0
    _total = len(_test_nodes)
    for _i, _node in enumerate(_test_nodes, 1):
        _source = _segment(_node)
        try:
            exec(compile(_source, f"<test-{_i}>", "exec"), _TEST_NS, _TEST_NS)
            _passed += 1
            _status = "PASS"
            _detail = ""
        except Exception as _exc:
            _status = "FAIL"
            _detail = (str(_exc) or _source).splitlines()[0][:400]
            _detail = f"{type(_exc).__name__}: {_detail}"
        print(f"__DSIR_TEST__:{_RUN_TOKEN}:{_i}:{_status}:{_detail or _source}", file=sys.stderr)
    print(f"__DSIR_RESULT__:{_RUN_TOKEN}:{_passed}:{_total}:{_total - _passed}", file=sys.stderr)

# Anything learner code prints during interpreter shutdown (for example a
# __del__ method) stays on the limited stdout stream.
sys.stdout = _LIMITED
'''
    return (
        template.replace("__IMPORTS__", module_imports)
        .replace("__SAFE__", repr(sorted(SAFE_BUILTINS)))
        .replace("__RUN_TOKEN__", repr(run_token))
        .replace("__OUTPUT_LIMIT__", str(MAX_OUTPUT_BYTES))
        .replace("__LEARNER_MAP__", learner_map)
        .replace("__TEST_MAP__", test_map)
        .replace("__USER_CODE__", repr(user_code))
        .replace("__TEST_CODE__", repr(test_code))
    )


def run_tests(code: str, test_code: str) -> dict[str, Any]:
    if not isinstance(code, str) or len(code.encode("utf-8")) > MAX_CODE_BYTES:
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": "Code exceeds the 64 KB limit."}
    if not isinstance(test_code, str) or not test_code.strip():
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": "Exercise has no valid tests."}

    try:
        _validate_ast(code)
    except UnsafeCode as exc:
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": str(exc)}

    try:
        _validate_ast(test_code, TEST_MODULES, strict=False)
    except UnsafeCode as exc:
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": f"Invalid exercise tests: {exc}"}

    run_token = secrets.token_hex(12)
    with tempfile.TemporaryDirectory(prefix="dsir-run-") as tmp:
        script = Path(tmp) / "runner.py"
        script.write_text(_runner_source(code, test_code, run_token), encoding="utf-8")
        env = {
            "PATH": "/usr/bin:/bin",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-B", str(script)],
                cwd=tmp,
                env=env,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                stdin=subprocess.DEVNULL,
                preexec_fn=_preexec_limits if os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired:
            return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": "Execution timed out after 3 seconds."}
        except Exception as exc:
            return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": f"Sandbox error: {type(exc).__name__}: {exc}"}

    stdout = proc.stdout[:MAX_OUTPUT_BYTES]
    stderr = proc.stderr[:MAX_OUTPUT_BYTES]
    details = []
    passed = failed = total = 0
    # The run token makes the result channel unforgeable: learner output that
    # imitates the protocol is ignored because it cannot know the token.
    test_prefix = f"__DSIR_TEST__:{run_token}:"
    result_prefix = f"__DSIR_RESULT__:{run_token}:"
    for line in stderr.splitlines():
        if line.startswith(test_prefix):
            rest = line[len(test_prefix):]
            parts = rest.split(":", 2)
            if len(parts) >= 2 and parts[0].isdigit():
                number = int(parts[0])
                ok = parts[1] == "PASS"
                detail = {"test": number, "passed": ok}
                if not ok and len(parts) >= 3 and parts[2]:
                    detail["error"] = parts[2]
                details.append(detail)
        elif line.startswith(result_prefix):
            parts = line[len(result_prefix):].split(":")
            if len(parts) == 3 and all(part.isdigit() for part in parts):
                passed, total, failed = map(int, parts)

    # Keep only genuine diagnostics; protocol lines are not errors.
    diagnostics = "\n".join(
        line for line in stderr.splitlines()
        if not line.startswith(("__DSIR_TEST__:", "__DSIR_RESULT__:"))
    ).strip()

    if proc.returncode != 0 and not total:
        if proc.returncode == -signal.SIGXCPU:
            return {
                "passed": 0,
                "failed": 1,
                "total": 1,
                "details": [],
                "error": f"Execution timed out after {TIMEOUT_SECONDS} seconds.",
            }
        error = (diagnostics or stdout.strip() or f"Process exited with code {proc.returncode}")[:2000]
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": error}

    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "details": details[:100],
        "error": diagnostics[:2000] if diagnostics else None,
        "output": stdout[:MAX_OUTPUT_BYTES],
    }
