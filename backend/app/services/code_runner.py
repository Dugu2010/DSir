"""Hardened Python practice runner.

Untrusted learner code is executed only in a short-lived child process with
strict resource limits and a deliberately tiny import/builtin surface. This
module is for practice grading only; it must never be used for arbitrary
server jobs.
"""

from __future__ import annotations

import ast
import os
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
    "abs", "all", "any", "bool", "bytes", "chr", "dict", "enumerate", "filter",
    "float", "format", "hash", "hex", "int", "isinstance", "issubclass", "iter",
    "len", "list", "map", "max", "min", "next", "ord", "pow", "print", "range",
    "repr", "reversed", "round", "set", "slice", "sorted", "str", "sum", "tuple",
    "type", "zip",
}


class UnsafeCode(ValueError):
    pass


def _validate_ast(code: str) -> None:
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise UnsafeCode(f"SyntaxError: {exc.msg} (line {exc.lineno})") from exc

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = node.names if isinstance(node, ast.Import) else [node]
            for item in names:
                module = getattr(item, "name", "").split(".")[0]
                if module not in {"math", "random"}:
                    raise UnsafeCode(f"Import '{module}' is not allowed in the practice sandbox.")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_NAMES:
                raise UnsafeCode(f"'{node.func.id}' is not allowed in the practice sandbox.")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise UnsafeCode(f"'{node.id}' is not allowed in the practice sandbox.")
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


def _runner_source(user_code: str, test_code: str) -> str:
    # The child receives a safe builtin allowlist and a restricted importer.
    # Tests run after learner code in the same namespace, but are never allowed
    # to expand the sandbox capabilities.
    return f'''import builtins\nimport math\nimport random\n\n_SAFE = {sorted(SAFE_BUILTINS)!r}\n_ALLOWED_MODULES = {{"math": math, "random": random}}\n\ndef _safe_import(name, globals=None, locals=None, fromlist=(), level=0):\n    root = name.split(".")[0]\n    if root not in _ALLOWED_MODULES:\n        raise ImportError(f"Import '{{name}}' is not allowed in the practice sandbox.")\n    return _ALLOWED_MODULES[root]\n\n_SAFE_BUILTINS = {{name: getattr(builtins, name) for name in _SAFE}}\n_SAFE_BUILTINS["__import__"] = _safe_import\n\n_NS = {{"__builtins__": _SAFE_BUILTINS}}\n\n# Learner code\nexec(compile({user_code!r}, "<learner>", "exec"), _NS, _NS)\n\n# Test setup + individual assertions.\n_TEST = {test_code!r}\n_setup = []\n_assertions = []\nfor _line in _TEST.splitlines():\n    if _line.strip().startswith("assert "):\n        _assertions.append(_line.strip())\n    elif _line.strip() and not _line.strip().startswith("#"):\n        _setup.append(_line)\nif _setup:\n    exec(compile("\\n".join(_setup), "<tests>", "exec"), _NS, _NS)\n\nif not _assertions:\n    print("__DSIR_RESULT__:PASS:1:1")\nelse:\n    _passed = 0\n    _total = len(_assertions)\n    for _i, _assertion in enumerate(_assertions, 1):\n        try:\n            exec(compile(_assertion, f"<test-{{_i}}>", "exec"), _NS, _NS)\n            _passed += 1\n            print(f"__DSIR_TEST__:{{_i}}:PASS:{{_assertion}}")\n        except Exception as _exc:\n            print(f"__DSIR_TEST__:{{_i}}:FAIL:{{type(_exc).__name__}}:{{_exc}}")\n    print(f"__DSIR_RESULT__:{{_passed}}:{{_total}}:{{_total - _passed}}")\n'''


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
        _validate_ast(test_code)
    except UnsafeCode as exc:
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": f"Invalid exercise tests: {exc}"}

    with tempfile.TemporaryDirectory(prefix="dsir-run-") as tmp:
        script = Path(tmp) / "runner.py"
        script.write_text(_runner_source(code, test_code), encoding="utf-8")
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
    for line in stdout.splitlines():
        if line.startswith("__DSIR_TEST__:"):
            parts = line.split(":", 4)
            if len(parts) >= 4:
                number = int(parts[1])
                ok = parts[2] == "PASS"
                detail = {"test": number, "passed": ok}
                if not ok and len(parts) >= 5:
                    detail["error"] = parts[3] + ": " + parts[4]
                details.append(detail)
        elif line.startswith("__DSIR_RESULT__:"):
            parts = line.split(":")
            if len(parts) == 4:
                passed, total, failed = map(int, parts[1:4])

    if proc.returncode != 0 and not total:
        error = (stderr.strip() or stdout.strip() or f"Process exited with code {proc.returncode}")[:2000]
        return {"passed": 0, "failed": 1, "total": 1, "details": [], "error": error}

    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "details": details[:100],
        "error": stderr.strip()[:2000] if stderr.strip() else None,
        "output": stdout[:MAX_OUTPUT_BYTES],
    }
