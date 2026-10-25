"""Module 14 — Testing, clean code, and Git."""

MODULE = {
    "slug": "testing-git-professional-habits",
    "title": "Testing, Clean Code, and Git",
    "description": (
        "Turn working code into trustworthy code: unit tests, readable "
        "structure, meaningful names, and version control habits employers "
        "expect to see."
    ),
    "objectives": [
        "Write and run pytest tests",
        "Structure code so it is easy to test",
        "Apply naming and simplicity habits",
        "Use Git branches and meaningful commits",
    ],
    "estimated_duration_minutes": 110,
    "lessons": [
        {
            "slug": "unit-testing-with-pytest",
            "title": "Unit Testing with pytest",
            "description": (
                "Tests are executable expectations. Learn the arrange-act-assert "
                "pattern, edge cases, and how to test failure paths."
            ),
            "difficulty": "intermediate",
            "minutes": 55,
            "tags": ["python", "testing", "pytest", "quality"],
            "objectives": [
                "Write focused pytest test functions",
                "Cover normal, boundary, and error cases",
                "Use parametrize to remove repetition",
                "Explain what makes a test valuable",
            ],
            "resources": [
                {
                    "title": "pytest documentation",
                    "url": "https://docs.pytest.org/en/stable/",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — unittest (stdlib)",
                    "url": "https://docs.python.org/3/library/unittest.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Unit Testing with pytest

## Why tests exist

A test encodes what "correct" means so future changes cannot silently break it. Tests also document intent and make refactoring safe.

## Arrange, act, assert

```python
# calculator.py
def divide(a, b):
    if b == 0:
        raise ValueError("cannot divide by zero")
    return a / b
```

```python
# test_calculator.py
import pytest
from calculator import divide


def test_divide_returns_quotient():
    result = divide(10, 2)          # arrange + act
    assert result == 5              # assert


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        divide(1, 0)


def test_divide_handles_negatives():
    assert divide(-9, 3) == -3
```

Run with:

```bash
python -m pytest -q
```

## What to test

- The happy path.
- Boundaries: empty input, zero, one item, maximum values.
- Invalid input and expected exceptions.
- Behaviour you have already broken once (regression tests).

Do not chase 100% coverage. Chase confidence in the behaviour that matters.

## Parametrize

```python
import pytest


@pytest.mark.parametrize(
    "text,expected",
    [
        ("hello world", 2),
        ("", 0),
        ("one", 1),
        ("  spaced   out  ", 2),
    ],
)
def test_word_count(text, expected):
    assert len(text.split()) == expected
```

One test body, many cases, and a clear failure report per case.

## Test behaviour, not implementation

A test that asserts a private helper was called will break during a harmless refactor. A test that asserts the public result stays useful.

```python
# Fragile: couples to internals
# assert formatter._build_prefix() == ">>"

# Robust: checks observable output
assert format_message("hi") == ">> hi"
```

## Fixtures for shared setup

```python
import pytest


@pytest.fixture
def sample_user():
    return {"name": "Ada", "active": True}


def test_active_user(sample_user):
    assert sample_user["active"] is True
```

Use fixtures when setup is repeated or expensive, not to hide unclear test data.

## Common mistakes

- Testing several behaviours in one giant test so failures are ambiguous.
- Asserting on printed output instead of return values.
- Depending on the current date, network, or random values without control.
- Writing tests that pass no matter what the code does.
- Fixing a failing test by deleting the assertion.

## Guided practice

Write three tests for a `is_valid_email` function: a valid address, a missing `@`, and an empty string. Predict which will fail before you run them.

## Independent practice

Add tests for a function that splits a bill: normal split, rounding, zero people (should raise), and negative total (should raise).

## Summary

Tests are small, fast, repeatable checks. Arrange, act, assert. Cover boundaries and errors. Prefer public behaviour over internals. Run tests before every commit.

## Further reading

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [unittest](https://docs.python.org/3/library/unittest.html)
''',
            "exercises": [
                {
                    "title": "Write tests for a discount function",
                    "description": "Cover normal and boundary behaviour.",
                    "instructions": (
                        "The function apply_discount(price, percent) returns the "
                        "discounted price, rejects negative values with ValueError, "
                        "and rejects percentages above 100. Write assertions that "
                        "verify it, including a zero discount and a full discount."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def apply_discount(price, percent):\n    if price < 0 or percent < 0:\n        raise ValueError("negative values are not allowed")\n    if percent > 100:\n        raise ValueError("percent cannot exceed 100")\n    return round(price * (1 - percent / 100), 2)\n\n# Add assertions below\n',
                    "solution": 'def apply_discount(price, percent):\n    if price < 0 or percent < 0:\n        raise ValueError("negative values are not allowed")\n    if percent > 100:\n        raise ValueError("percent cannot exceed 100")\n    return round(price * (1 - percent / 100), 2)\n\nassert apply_discount(100, 20) == 80.0\nassert apply_discount(100, 0) == 100.0\nassert apply_discount(100, 100) == 0.0\nassert apply_discount(19.99, 10) == 17.99\ntry:\n    apply_discount(-1, 10)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\ntry:\n    apply_discount(10, 101)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\n',
                    "tests": 'assert apply_discount(100, 20) == 80.0\nassert apply_discount(100, 100) == 0.0\nassert apply_discount(50, 0) == 50.0\n',
                    "hints": [
                        "Assert exact rounded values.",
                        "Use try/except to check that invalid input raises.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "testing", "boundaries"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "clean-code-and-git-workflow",
            "title": "Clean Code and a Git Workflow",
            "description": (
                "Naming, function size, duplication, and a branch-and-commit "
                "loop that keeps history understandable."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "clean-code", "git", "github"],
            "objectives": [
                "Apply naming and single-responsibility habits",
                "Reduce duplication without premature abstraction",
                "Create branches and write meaningful commits",
            ],
            "resources": [
                {
                    "title": "Git documentation",
                    "url": "https://git-scm.com/doc",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — PEP 8 style guide",
                    "url": "https://peps.python.org/pep-0008/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Clean Code and a Git Workflow

## Names carry the design

```python
# Before
def calc(d, r):
    return d * (1 - r / 100)

# After
def apply_discount(price, percent_off):
    return price * (1 - percent_off / 100)
```

If a name needs a comment to explain it, rename it instead.

## One job per function

```python
# Mixed responsibilities
def process_orders(rows):
    total = 0
    for row in rows:
        total += float(row[2])
    with open("report.txt", "w") as file:
        file.write(str(total))
    return total
```

Split reading, calculating, and writing:

```python
def parse_amounts(rows):
    return [float(row[2]) for row in rows]


def total_amount(rows):
    return sum(parse_amounts(rows))


def write_report(path, total):
    with open(path, "w") as file:
        file.write(f"total: {total:.2f}")
```

Each piece is testable in isolation.

## Comments explain why, not what

```python
# Bad: restates the code
count += 1  # increment count

# Good: records a non-obvious constraint
# The API returns cents, so divide only when displaying currency.
```

## Duplication and the rule of three

Copying once may be fine. After the third repetition, extract a function — but only if the copies represent the same concept. Two lookalike blocks that change for different reasons should stay separate.

## Git basics

```bash
git status
git diff
git log --oneline -5
```

A small feature:

```bash
git switch -c feature/expense-totals
# edit, test
git add expenses.py tests/test_expenses.py
git commit -m "Add monthly totals with float-safe rounding"
git push -u origin feature/expense-totals
```

Then open a pull request, describe **why**, and note how you tested it.

## Commit messages

A useful message states the change and its purpose:

```
Reject zero-quantity orders

The checkout endpoint accepted quantity=0, creating empty shipments.
Validate before persisting and cover it with a regression test.
```

Avoid `fix`, `update`, `changes`, `final`, `final2`.

## What not to commit

- `.env` files and API keys.
- `__pycache__`, virtual environments, build output.
- Large data dumps.
- Editor-specific settings unless the team agrees.

Use `.gitignore` and check `git status` before committing.

## Code review habits

- Read your own diff before asking someone else to.
- Keep pull requests small enough to review in one sitting.
- Ask questions about intent rather than style preferences.
- Run tests locally first.

## Summary

Clean code is code a tired teammate can change safely. Clear names, small functions, honest comments, and a tidy Git history are professional communication, not decoration.

## Further reading

- [Git documentation](https://git-scm.com/doc)
- [PEP 8](https://peps.python.org/pep-0008/)
''',
            "exercises": [
                {
                    "title": "Refactor for clarity",
                    "description": "Rename and split without changing behaviour.",
                    "instructions": (
                        "Refactor process(data) into two functions: clean_names(names) "
                        "that strips and title-cases non-empty names, and "
                        "summarize(names) that returns a string like "
                        "'3 students: Ada, Grace, Linus'. Keep the tests passing."
                    ),
                    "type": "refactoring",
                    "difficulty": "medium",
                    "starter": 'def process(data):\n    out = []\n    for d in data:\n        d = d.strip()\n        if d:\n            out.append(d.title())\n    return out\n\n\ndef summarize(data):\n    names = process(data)\n    return f"{len(names)} students: " + ", ".join(names)\n',
                    "solution": 'def clean_names(names):\n    cleaned = []\n    for name in names:\n        stripped = name.strip()\n        if stripped:\n            cleaned.append(stripped.title())\n    return cleaned\n\n\ndef summarize(names):\n    cleaned = clean_names(names)\n    joined = ", ".join(cleaned)\n    return f"{len(cleaned)} students: {joined}"\n',
                    "tests": 'assert clean_names([" ada ", "", "grace "]) == ["Ada", "Grace"]\nassert summarize(["ada", "grace", "linus"]) == "3 students: Ada, Grace, Linus"\nassert summarize([]) == "0 students: "\n',
                    "hints": [
                        "Return the cleaned list from the first function.",
                        "Build the sentence from the cleaned list in the second.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "refactoring", "clean-code"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 14 Assessment — Testing and Git",
        "description": "Check test design, naming, and version control habits.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What is the main purpose of a unit test?",
                "options": [
                    ("To lock in expected behaviour so changes can be verified", True),
                    ("To increase the line count", False),
                    ("To replace documentation entirely", False),
                    ("To make code run faster", False),
                ],
                "explanation": "Tests give fast, repeatable evidence that behaviour still holds.",
            },
            {
                "content": "Which test is most valuable?",
                "options": [
                    ("A boundary case that previously caused a bug", True),
                    ("A test that asserts True", False),
                    ("A test of a private helper's call count", False),
                    ("A test that requires the network", False),
                ],
                "explanation": "Regression tests for real failures protect the behaviour that matters.",
            },
            {
                "content": "Which file should never be committed?",
                "options": [(".env with secrets", True), ("README.md", False), ("tests/test_app.py", False), (".gitignore", False)],
                "explanation": "Secrets belong in environment configuration, never in version control.",
            },
            {
                "content": "What makes a commit message useful?",
                "options": [
                    ("It explains what changed and why", True),
                    ("It is always one word", False),
                    ("It lists every file touched", False),
                    ("It says 'final'", False),
                ],
                "explanation": "Future readers need the intent, not a file inventory.",
            },
        ],
    },
    "projects": [],
}
