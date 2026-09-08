"""Real code execution for exercise grading.

The normal learner editor runs code in the browser. This module exists only for
server-side submission grading and therefore treats submitted code as hostile.
It is hardened with resource limits, isolated temporary working directories,
a minimal environment, process-group cleanup, and per-worker concurrency caps.

Important: subprocess + rlimits are NOT a complete security boundary. A truly
untrusted production grader should run in a separately isolated container or
microVM with no network and a read-only host filesystem.
"""

import os
import shutil
import signal
import subprocess
import tempfile
import threading
import structlog
from typing import Optional

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

_INTERPRETERS = {
    "python": ["python3", "python"],
    "javascript": ["node"],
    "js": ["node"],
}
_MAX_CODE_BYTES = 512 * 1024
_MAX_TEST_BYTES = 512 * 1024
_MAX_TIMEOUT = max(1, min(settings.SANDBOX_MAX_EXECUTION_TIME, 30))
_MAX_CONCURRENT = max(1, settings.SANDBOX_MAX_CONCURRENT)
_EXECUTION_SLOTS = threading.BoundedSemaphore(_MAX_CONCURRENT)


def _find_interpreter(language: str) -> Optional[str]:
    for candidate in _INTERPRETERS.get(language.lower(), []):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def _set_limits():
    """Apply resource limits in the child process (POSIX only)."""
    if os.name == "nt":
        return
    import resource

    memory = max(64, settings.SANDBOX_MAX_MEMORY_MB) * 1024 * 1024
    cpu = min(5, _MAX_TIMEOUT)
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NPROC, (20, 20))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _extract_asserts(test_code: str) -> list[str]:
    asserts = []
    for raw in (test_code or "").splitlines():
        line = raw.strip()
        if line.startswith("assert ") and not line.startswith("#"):
            asserts.append(line)
    return asserts


def _safe_environment(tmp_path: str) -> dict[str, str]:
    # Never expose Render secrets, database URLs, API keys, Redis credentials,
    # or the application's normal HOME/PYTHONPATH to learner code.
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": tmp_path,
        "TMPDIR": tmp_path,
        "TEMP": tmp_path,
        "TMP": tmp_path,
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_NO_WARNINGS": "1",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    }


def _terminate_process_group(proc: subprocess.Popen) -> None:
    try:
        if os.name != "nt":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except (ProcessLookupError, OSError):
        pass


def _run_script(interpreter: str, script: str, timeout: int, suffix: str):
    if len(script.encode("utf-8", errors="ignore")) > _MAX_CODE_BYTES + _MAX_TEST_BYTES:
        return False, "", "Submission is too large"

    tmp_dir = tempfile.mkdtemp(prefix="dsir-sandbox-")
    tmp_path = os.path.join(tmp_dir, "main" + suffix)
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(script)

        try:
            with _EXECUTION_SLOTS:
                proc = subprocess.Popen(
                    [interpreter, tmp_path],
                    cwd=tmp_dir,
                    env=_safe_environment(tmp_dir),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    start_new_session=(os.name != "nt"),
                    preexec_fn=_set_limits if os.name != "nt" else None,
                )
                try:
                    stdout, stderr = proc.communicate(timeout=max(1, min(timeout, _MAX_TIMEOUT)))
                except subprocess.TimeoutExpired:
                    _terminate_process_group(proc)
                    stdout, stderr = proc.communicate()
                    return False, stdout[-100_000:], "Execution timed out"
        except Exception as exc:
            logger.warning("sandbox execution failed", error=str(exc)[:200])
            return False, "", str(exc)

        stdout = (stdout or "")[-100_000:]
        stderr = (stderr or "")[-100_000:]
        if proc.returncode == 0:
            return True, stdout, None

        err = (stderr or stdout or "").strip()
        if "AssertionError" in err:
            return False, stdout, "Test failed"
        return False, stdout, err[:100_000]
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def run_tests(code: str, language: str, test_code: str, timeout: int = 10) -> dict:
    """Run learner code against test assertions without exposing the tests."""
    language = (language or "python").lower()
    if len((code or "").encode("utf-8", errors="ignore")) > _MAX_CODE_BYTES:
        return {"passed": 0, "failed": 0, "total": 0, "details": [], "error": "Submission is too large"}
    if len((test_code or "").encode("utf-8", errors="ignore")) > _MAX_TEST_BYTES:
        logger.error("Exercise test code exceeds sandbox limit", language=language)
        return {"passed": 0, "failed": 0, "total": 0, "details": [], "error": "Exercise tests are too large"}

    interpreter = _find_interpreter(language)
    if interpreter is None:
        return {"passed": 0, "failed": 0, "total": 0, "details": [], "error": f"No runtime available for '{language}'"}

    timeout = max(1, min(timeout, _MAX_TIMEOUT))
    if language == "python":
        return _run_python(interpreter, code, test_code, timeout)
    if language in ("javascript", "js"):
        return _run_javascript(interpreter, code, test_code, timeout)
    return {"passed": 0, "failed": 0, "total": 0, "details": [], "error": f"Unsupported language: {language}"}


def _run_python(interpreter: str, code: str, test_code: str, timeout: int) -> dict:
    asserts = _extract_asserts(test_code)
    details = []
    passed = 0
    error = None

    if not asserts:
        ok, output, err = _run_script(interpreter, code + "\n", timeout, ".py")
        details.append({"test": "Execution", "passed": ok, "output": output, "error": err})
        if ok:
            passed = 1
        else:
            error = err
    else:
        for index, statement in enumerate(asserts, start=1):
            script = f"{code}\n\n{statement}\n"
            ok, output, err = _run_script(interpreter, script, timeout, ".py")
            details.append({"test": f"Test {index}", "passed": ok, "output": output, "error": err})
            if ok:
                passed += 1
            elif error is None:
                error = err

    total = len(details)
    return {"passed": passed, "failed": total - passed, "total": total, "details": details, "error": error}


def _run_javascript(interpreter: str, code: str, test_code: str, timeout: int) -> dict:
    script = f"{code}\n{test_code}\n"
    ok, output, err = _run_script(interpreter, script, timeout, ".js")
    details = [{"test": "Execution", "passed": ok, "output": output, "error": err}]
    return {"passed": 1 if ok else 0, "failed": 0 if ok else 1, "total": 1, "details": details, "error": err}
