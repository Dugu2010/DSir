"""Security and correctness checks for the practice code runner.

The runner executes untrusted learner code, so these tests focus on the
boundaries: forbidden capabilities, resource limits, and the impossibility of
forging a passing result from learner output.
"""

from app.services import code_runner


def test_legitimate_solution_passes_its_tests():
    result = code_runner.run_tests(
        "def add(a, b):\n    return a + b\n",
        "assert add(2, 3) == 5\nassert add(-1, 1) == 0\n",
    )
    assert result["passed"] == 2
    assert result["total"] == 2
    assert result["error"] is None


def test_failing_assertion_is_reported_with_the_source_line():
    result = code_runner.run_tests(
        "def add(a, b):\n    return a - b\n",
        "assert add(2, 3) == 5\n",
    )
    assert result["passed"] == 0
    assert result["failed"] == 1
    assert result["details"][0]["passed"] is False
    assert "AssertionError" in result["details"][0]["error"]
    assert "add(2, 3)" in result["details"][0]["error"]


def test_stdlib_imports_outside_the_allowlist_are_rejected():
    result = code_runner.run_tests("import os\n", "assert True\n")
    assert result["passed"] == 0
    assert "not allowed" in result["error"]


def test_filesystem_access_is_rejected_even_through_io():
    for code in (
        "open('/etc/passwd').read()\n",
        "import io\nio.open('/etc/passwd')\n",
        "from pathlib import Path\n",
    ):
        result = code_runner.run_tests(code, "assert True\n")
        assert result["passed"] == 0, code
        assert result["error"], code


def test_shutdown_output_cannot_forge_a_passing_result():
    """A `__del__` runs after the harness, but the run token protects it."""
    result = code_runner.run_tests(
        "class Sneaky:\n"
        "    def __del__(self):\n"
        "        print('__DSIR_RESULT__:1:1:0')\n"
        "        print('__DSIR_TEST__:1:PASS:fake')\n"
        "sneaky = Sneaky()\n",
        "assert False\n",
    )
    assert result["passed"] == 0
    assert result["failed"] == 1
    assert result["total"] == 1


def test_stdout_flood_is_capped_without_losing_the_result():
    result = code_runner.run_tests(
        "for _ in range(200_000):\n    print('x' * 100)\n",
        "assert True\n",
    )
    assert result["passed"] == 1
    assert result["total"] == 1
    assert len(result["output"]) <= code_runner.MAX_OUTPUT_BYTES


def test_infinite_loop_hits_the_timeout(monkeypatch):
    monkeypatch.setattr(code_runner, "TIMEOUT_SECONDS", 1)
    result = code_runner.run_tests("while True:\n    pass\n", "assert True\n")
    assert result["passed"] == 0
    assert "timed out" in result["error"].lower()
