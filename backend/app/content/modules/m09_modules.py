"""Module 9 — Modules and environments."""

MODULE = {
    "slug": "modules-and-environments",
    "title": "Modules, Packages, and Virtual Environments",
    "description": (
        "Stop putting every line in one file. Split code into modules, use the "
        "standard library, install third-party packages safely, and isolate "
        "projects with virtual environments."
    ),
    "objectives": [
        "Import modules and specific names",
        "Explain __name__ == '__main__'",
        "Create a small package with multiple modules",
        "Create a virtual environment and install a dependency",
    ],
    "estimated_duration_minutes": 95,
    "lessons": [
        {
            "slug": "imports-modules-standard-library",
            "title": "Imports, Modules, and the Standard Library",
            "description": (
                "Use Python's batteries-included library and learn the import "
                "styles that keep dependencies obvious."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "modules", "imports", "standard-library"],
            "objectives": [
                "Import a module and call its functions",
                "Import specific names with from ... import",
                "Explain why wildcard imports are discouraged",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Modules",
                    "url": "https://docs.python.org/3/tutorial/modules.html",
                    "resource_type": "reference",
                },
                {
                    "title": "Python Standard Library",
                    "url": "https://docs.python.org/3/library/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Imports, Modules, and the Standard Library

## A module is a file of Python code

Create `math_tools.py`:

```python
def double(number):
    return number * 2


PI_APPROX = 3.14159
```

Use it from another file in the same folder:

```python
import math_tools

print(math_tools.double(5))
print(math_tools.PI_APPROX)
```

The module name is the filename without `.py`.

## Import styles

```python
import math
print(math.sqrt(16))

from math import sqrt, pi
print(sqrt(25))

import random as rnd
print(rnd.randint(1, 6))
```

Prefer `import math` when you want the source of every name to be obvious. `from math import sqrt` is fine when the name is unambiguous.

Avoid:

```python
from math import *
```

It hides where names came from and can overwrite yours.

## The standard library is enormous

```python
import json
import re
import statistics
from datetime import date, timedelta
from collections import Counter
```

These are included with Python. Before installing a dependency, check whether the standard library already solves the problem. Reading the [library index](https://docs.python.org/3/library/) is a real skill.

`Counter` is especially useful:

```python
from collections import Counter

counts = Counter("banana")
print(counts["a"])        # 3
print(counts.most_common(1))  # [('a', 3)]
```

## `__name__` and entry points

```python
def main():
    print("Running the program")


if __name__ == "__main__":
    main()
```

When the file is run directly, `__name__` is `"__main__"`. When it is imported, `__name__` is the module name, so `main()` does not run automatically. This lets a file be both a library and a script.

## Module search path

Python looks in the current directory, installed library paths, and the `PYTHONPATH`. A common import error is simply running from the wrong directory or having two files with the same name.

## Common mistakes

- Naming a file `random.py` or `json.py`, which shadows the standard library.
- Using wildcard imports.
- Assuming import order does not matter; imports execute top-level code.
- Importing a module that is not installed and confusing it with a standard module.

## Guided practice

Predict the output:

```python
import math
from math import floor

print(math.ceil(2.1))
print(floor(2.9))
```

Expected `3` and `2`.

## Independent practice

Create `text_tools.py` with `word_count` and `initials` functions. Import it from `app.py`, run both, then import `app` from another file and observe that `main()` does not run if guarded.

## Summary

Modules split code into files. Imports make dependencies visible. The standard library solves many problems before a third-party package is needed. Use the `__main__` guard for runnable modules.

## Further reading

- [Python Tutorial — Modules](https://docs.python.org/3/tutorial/modules.html)
- [Standard Library index](https://docs.python.org/3/library/)
''',
            "exercises": [
                {
                    "title": "Hypotenuse with math",
                    "description": "Use a standard-library module instead of reimplementing maths.",
                    "instructions": (
                        "Complete hypotenuse(a, b) using math.hypot or sqrt. "
                        "Round the result to two decimal places."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'import math\n\n\ndef hypotenuse(a, b):\n    pass\n',
                    "solution": 'import math\n\n\ndef hypotenuse(a, b):\n    return round(math.sqrt(a ** 2 + b ** 2), 2)\n',
                    "tests": 'assert hypotenuse(3, 4) == 5.0\nassert hypotenuse(5, 12) == 13.0\nassert hypotenuse(1, 1) == 1.41\n',
                    "hints": [
                        "The Pythagorean theorem is a² + b² = c².",
                        "math.sqrt returns a float; round it.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "modules", "math"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "packages-pip-virtual-environments",
            "title": "Packages, pip, and Virtual Environments",
            "description": (
                "Structure a multi-file package, install dependencies, and keep "
                "projects isolated so they do not break each other."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "packages", "pip", "venv", "dependencies"],
            "objectives": [
                "Create a package directory with __init__.py",
                "Create and activate a virtual environment",
                "Install and record dependencies with pip",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Packages",
                    "url": "https://docs.python.org/3/tutorial/modules.html#packages",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — venv",
                    "url": "https://docs.python.org/3/library/venv.html",
                    "resource_type": "reference",
                },
                {
                    "title": "pip documentation",
                    "url": "https://pip.pypa.io/en/stable/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Packages, pip, and Virtual Environments

## A package is a folder of modules

```text
textkit/
    __init__.py
    clean.py
    stats.py
app.py
```

```python
# textkit/clean.py
def normalise(text):
    return " ".join(text.lower().split())
```

```python
# app.py
from textkit.clean import normalise

print(normalise("  Hello   World "))
```

```text
hello world
```

`__init__.py` marks the folder as a package. It can be empty, or it can expose a small public API.

## Why virtual environments matter

Different projects need different library versions. Installing everything globally creates conflicts that are painful to diagnose.

```bash
# create
python -m venv .venv

# activate (Linux/macOS)
source .venv/bin/activate

# activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# confirm
python --version
```

When active, `python` and `pip` refer to the environment. Deactivate with `deactivate`.

## Installing dependencies

```bash
pip install requests
pip freeze > requirements.txt
```

To reproduce an environment:

```bash
pip install -r requirements.txt
```

Pin versions in real projects. “Latest” changes; a tested version does not.

## Never commit `.venv`

Add it to `.gitignore`:

```text
.venv/
__pycache__/
*.pyc
```

Commit `requirements.txt` or `pyproject.toml` instead. The environment can be recreated; it should not be shared as source.

## Imports inside a package

Prefer absolute imports:

```python
from textkit.stats import word_count
```

Relative imports (`from .stats import word_count`) are valid inside packages but can surprise beginners. Choose one style and stay consistent.

## Common mistakes

- Installing packages without activating the environment.
- Committing the virtual environment directory.
- Naming a project file `json.py` and shadowing the standard library.
- Forgetting `__init__.py` (namespace packages exist, but explicit packages are easier to reason about).
- Adding a package for a problem the standard library already solves.

## Guided practice

Create a virtual environment, activate it, install `requests`, and run `pip show requests`. Then deactivate and notice that `python -c "import requests"` may fail outside the environment.

## Independent practice

Build a `textkit` package with `clean.py` and `stats.py`. Import both from `app.py`. Add a `requirements.txt` even if it contains no third-party packages.

## Summary

A package organises modules. A virtual environment isolates dependencies per project. `pip install` changes an environment; `requirements.txt` records what is needed elsewhere.

## Further reading

- [Python Tutorial — Packages](https://docs.python.org/3/tutorial/modules.html#packages)
- [venv documentation](https://docs.python.org/3/library/venv.html)
- [pip documentation](https://pip.pypa.io/en/stable/)
''',
            "exercises": [],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 9 Assessment — Modules and Environments",
        "description": "Check imports, package structure, and dependency isolation.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What does `if __name__ == \"__main__\":` guard?",
                "options": [
                    ("Code that should run only when the file is executed directly", True),
                    ("Code that should never run", False),
                    ("Code that only runs in the REPL", False),
                    ("An import error handler", False),
                ],
                "explanation": "Imported modules have their own __name__, so the guarded block is skipped.",
            },
            {
                "content": "Why should `.venv/` usually be excluded from Git?",
                "options": [
                    ("It contains machine-specific installed packages and can be recreated", True),
                    ("Git cannot store folders", False),
                    ("It makes Python slower", False),
                    ("Virtual environments are secret", False),
                ],
                "explanation": "The environment is disposable; requirements files record how to rebuild it.",
            },
            {
                "content": "Which import is clearest in a code review?",
                "options": [
                    ("import statistics", True),
                    ("from statistics import *", False),
                    ("import stats", False),
                    ("from * import statistics", False),
                ],
                "explanation": "A plain module import makes the source of names obvious.",
            },
        ],
    },
    "projects": [],
}
