"""Real code execution for exercise grading.

Runs learner-submitted code in a subprocess (not keyword matching) and
evaluates it against the exercise's test assertions. Uses resource limits
and timeouts so a bad submission can't hang the server.
"""

import os
import shutil
import subprocess
import tempfile
import structlog
from typing import Optional

logger = structlog.get_logger()

# Map language → interpreter binary (falling back to what's installed).
_INTERPRETERS = {
    "python": ["python3", "python"],
    "javascript": ["node"],
    "js": ["node"],
}


def _find_interpreter(language: str) -> Optional[str]:
    for candidate in _INTERPRETERS.get(language.lower(), []):
        path = shutil.which(candidate)
        if path:
            return candidate
    return None


def _set_limits():
    """Apply resource limits in the child process (POSIX only)."""
    if os.name == "nt":
        return
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
    except Exception:  # pragma: no cover - non-fatal on exotic systems
        pass


def _extract_asserts(test_code: str) -> list[str]:
    """Pull individual assert statements out of the test code."""
    asserts = []
    for raw in (test_code or "").split("\n"):
        line = raw.strip()
        if line.startswith("assert ") and not line.startswith("#"):
            asserts.append(line)
    return asserts


def _run_script(interpreter: str, script: str, timeout: int, suffix: str):
    """Execute a script in a subprocess; return (passed, output, error)."""
    fd, tmp_path = tempfile.mkstemp(suffix=suffix, text=True)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        proc = subprocess.run(
            [interpreter, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            preexec_fn=_set_limits if os.name != "nt" else None,
        )
        if proc.returncode == 0:
            return True, proc.stdout, None
        err = (proc.stderr or proc.stdout or "").strip()
        if "AssertionError" in err:
            return False, proc.stdout, err.splitlines()[-1] if err.splitlines() else None
        return False, proc.stdout, err
    except subprocess.TimeoutExpired:
        return False, "", "Execution timed out"
    except Exception as e:  # pragma: no cover
        return False, "", str(e)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def run_tests(code: str, language: str, test_code: str, timeout: int = 10) -> dict:
    """Run learner code against test assertions.

    Returns a dict shaped like the Submission.test_results payload:
    {passed, failed, total, details: [{test, passed, output, error}]}.
    """
    language = (language or "python").lower()
    interpreter = _find_interpreter(language)
    if interpreter is None:
        return {
            "passed": 0, "failed": 0, "total": 0,
            "details": [],
            "error": f"No runtime available for '{language}'",
        }

    if language in ("python",):
        return _run_python(interpreter, code, test_code, timeout)
    if language in ("javascript", "js"):
        return _run_javascript(interpreter, code, test_code, timeout)
    return {
        "passed": 0, "failed": 0, "total": 0,
        "details": [], "error": f"Unsupported language: {language}",
    }


def _run_python(interpreter: str, code: str, test_code: str, timeout: int) -> dict:
    asserts = _extract_asserts(test_code)
    details = []
    passed = 0
    error = None

    if not asserts:
        ok, output, err = _run_script(
            interpreter, code + "\n", timeout, suffix=".py"
        )
        details.append({"test": "(code executes without error)", "passed": ok, "output": output, "error": err})
        if ok:
            passed = 1
        else:
            error = err
    else:
        for statement in asserts:
            script = f"{code}\n\n{statement}\n"
            ok, output, err = _run_script(interpreter, script, timeout, suffix=".py")
            details.append({"test": statement, "passed": ok, "output": output, "error": err})
            if ok:
                passed += 1
            elif error is None:
                error = err

    total = len(details)
    failed = total - passed
    return {
        "passed": passed,
        "failed": failed,
        "total": total,
        "details": details,
        "error": error,
    }


def _run_javascript(interpreter: str, code: str, test_code: str, timeout: int) -> dict:
    """Run JS code; the test_code is appended and console output captured."""
    script = f"{code}\n{test_code}\n"
    ok, output, err = _run_script(interpreter, script, timeout, suffix=".js")
    details = [{
        "test": "(script executes without error)",
        "passed": ok,
        "output": output,
        "error": err,
    }]
    return {
        "passed": 1 if ok else 0,
        "failed": 0 if ok else 1,
        "total": 1,
        "details": details,
        "error": err,
    }
