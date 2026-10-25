"""Module 2 — Setup, tools, and a reliable first workflow."""

MODULE = {
    "slug": "setup-and-first-programs",
    "title": "Installation, Tools, and First Programs",
    "description": (
        "Get a working Python installation, understand the tools you will use "
        "every day, and build a repeatable write-run-fix workflow that works on "
        "Windows, macOS, and Linux."
    ),
    "objectives": [
        "Install Python and verify the version from a terminal",
        "Choose and configure a beginner-friendly editor",
        "Run code in the REPL, a script, and an editor",
        "Use comments, blank lines, and naming conventions to keep code readable",
    ],
    "estimated_duration_minutes": 85,
    "lessons": [
        {
            "slug": "installing-python-and-choosing-an-editor",
            "title": "Installing Python and Choosing an Editor",
            "description": (
                "A calm setup guide: install Python, verify it, and configure one "
                "editor instead of collecting tools you never use."
            ),
            "difficulty": "beginner",
            "minutes": 35,
            "tags": ["python", "installation", "tools", "environment"],
            "objectives": [
                "Install or verify Python 3.10+ on your system",
                "Explain the difference between python and python3",
                "Run a file with an absolute or relative path",
            ],
            "resources": [
                {
                    "title": "Python.org — Download Python",
                    "url": "https://www.python.org/downloads/",
                    "resource_type": "download",
                },
                {
                    "title": "Python.org — Getting Started",
                    "url": "https://www.python.org/about/gettingstarted/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Installing Python and Choosing an Editor

## What you need

You need three things, and no more:

1. A Python interpreter (version **3.10 or newer**; this course is verified on 3.12).
2. A terminal where you can run commands.
3. One editor that can save plain text files.

You do **not** need five IDEs, a paid course, or a perfect setup. A working setup beats an ideal one you never finish.

## Install Python

Download the official installer from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick **“Add python.exe to PATH”** during installation. On macOS, the python.org installer is usually smoother than relying on a system Python. On Linux, use your distribution's package manager if it provides Python 3.10+.

Verify it in a terminal:

```bash
python --version
```

On many systems the command is:

```bash
python3 --version
```

Expected output (your patch version may differ):

```text
Python 3.12.4
```

If neither command works, close and reopen the terminal so it picks up the updated PATH. If you see “command not found”, the interpreter is installed but not on PATH — fix that before continuing.

## Pick one editor

You only need syntax highlighting, a file tree, and a terminal. Good beginner choices include VS Code, Thonny, or PyCharm Community. Use one for at least this module. Constantly changing tools is procrastination disguised as preparation.

Create a folder called `python-learning` and keep every practice file there. A predictable folder makes paths easier to understand.

## Run your first file

Create `hello.py`:

```python
# My first saved program
print("Hello from a file")
```

From the folder that contains the file:

```bash
python hello.py
```

The terminal's **current working directory** matters. If you run the command from a different folder, Python cannot find `hello.py`. This is one of the most common beginner problems.

## Comments

Comments start with `#` and are ignored by Python:

```python
# This explains why the next line exists
total = 10 + 5
```

Good comments explain *why*. They do not narrate obvious syntax.

## Common mistakes

- Installing Python but forgetting the PATH option on Windows.
- Saving a file without the `.py` extension.
- Running `python hello.py` from the wrong folder.
- Following a tutorial that uses Python 2 syntax such as `print "hello"`.

## Guided practice

Create a file with this content and run it:

```python
# A tiny setup check
print("Python is installed")
print("I can run a file")
```

Now rename the file, run it under the new name, and observe what happens if you use the old name. That error is a file-not-found error, not a Python language error.

## Summary

- Install Python 3.10+ from the official source.
- Verify with `--version`.
- Use one editor and one practice folder.
- The terminal's current directory is part of the program's context.

## Further reading

- [Python.org Downloads](https://www.python.org/downloads/)
- [Python.org Getting Started](https://www.python.org/about/gettingstarted/)
''',
            "exercises": [],
        },
        {
            "slug": "repl-scripts-and-a-reliable-workflow",
            "title": "REPL, Scripts, and a Reliable Workflow",
            "description": (
                "Use each tool for what it is good at, organise a tiny project, "
                "and build the habit of verifying every change."
            ),
            "difficulty": "beginner",
            "minutes": 30,
            "tags": ["python", "repl", "scripts", "workflow", "debugging"],
            "objectives": [
                "Choose the REPL or a script for a given task",
                "Run a script with a clear input and output",
                "Verify a change without breaking the rest of the file",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Using the Python Interpreter",
                    "url": "https://docs.python.org/3/tutorial/interpreter.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# REPL, Scripts, and a Reliable Workflow

## A tool for each job

Use the **REPL** when you want to test one idea quickly:

```text
>>> 17 * 3
51
>>> "py" + "thon"
'python'
```

Use a **script** when you want something you can keep, run repeatedly, and show to someone else.

This is not a personality test. Professionals move between both all day.

## A small, organised project

```text
python-learning/
    hello.py
    calculator.py
    notes.md
```

- `hello.py` is a script.
- `calculator.py` is another script.
- `notes.md` records what you learned in plain language.

That third file matters more than beginners expect. Writing an explanation exposes fuzzy understanding.

## Work in small verified steps

Start with:

```python
def rectangle_area(width, height):
    return width * height


print(rectangle_area(4, 5))
```

Run it. Expected output:

```text
20
```

Only then add a second case:

```python
print(rectangle_area(2.5, 4))
```

```text
10.0
```

You now have evidence that the function works for integers and floats. That is a tiny test, and it is the beginning of real testing practice.

## The loop

1. **Write** the smallest complete change.
2. **Run** the file.
3. **Observe** the output or error.
4. **Explain** why it happened.
5. **Change one thing** and repeat.

Do not skip step 4. Running code without explaining it produces familiarity without understanding.

## Common mistakes

- Writing an entire app before running anything.
- Leaving debugging `print()` calls in final code without a reason.
- Using a REPL for a long program and losing the code when the terminal closes.
- Treating a successful run as proof that all inputs work.

## Guided practice

Run this in the REPL and then in a file:

```python
print(3 * "ha")
```

Expected output:

```text
hahaha
```

Then predict `print("ha" * 3)` before running it. The result is the same here, but the mental model is different: string repetition.

### Hints

- Strings support `*` with an integer.
- `3 * "ha"` and `"ha" * 3` both repeat the string.

## Independent practice

Create `about_me.py` that defines a function `introduce(name, goal)` and returns a sentence containing both values. Print two different calls. Run the file after each change.

## Check yourself

- When is the REPL the better tool?
- Why does the terminal's working directory matter?
- What makes a code change “verified”?

## Summary

A professional workflow is deliberately boring: small edits, immediate runs, explicit explanations, and evidence before moving on.

## Further reading

- [Python Tutorial — Using the Python Interpreter](https://docs.python.org/3/tutorial/interpreter.html)
''',
            "exercises": [
                {
                    "title": "Rectangle area function",
                    "description": "Turn a calculation into a reusable, testable function.",
                    "instructions": (
                        "Complete rectangle_area(width, height) so it returns the "
                        "area. Do not print inside the function."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def rectangle_area(width, height):\n    # Return the area\n    pass\n',
                    "solution": 'def rectangle_area(width, height):\n    return width * height\n',
                    "tests": 'assert rectangle_area(4, 5) == 20\nassert rectangle_area(2.5, 4) == 10.0\nassert rectangle_area(0, 99) == 0\n',
                    "hints": [
                        "Area of a rectangle is width multiplied by height.",
                        "Use return, not print, so the result can be tested.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "functions", "arithmetic"],
                },
                {
                    "title": "Fix the indentation",
                    "description": "Read a traceback and repair a small block of code.",
                    "instructions": (
                        "The starter code raises an IndentationError. Fix it so "
                        "the function returns the total price including tax."
                    ),
                    "type": "debugging",
                    "difficulty": "easy",
                    "starter": 'def total_with_tax(price, tax_rate):\nreturn price * (1 + tax_rate)\n',
                    "solution": 'def total_with_tax(price, tax_rate):\n    return price * (1 + tax_rate)\n',
                    "tests": 'assert total_with_tax(100, 0.2) == 120.0\nassert round(total_with_tax(50, 0.1), 2) == 55.0\n',
                    "hints": [
                        "A function body must be indented.",
                        "Use four spaces for the return line.",
                    ],
                    "points": 10,
                    "minutes": 7,
                    "tags": ["python", "indentation", "debugging"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 2 Assessment — Setup and Workflow",
        "description": "Verify that your environment and working habits are solid.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Which command is the most reliable first check that Python is installed?",
                "options": [
                    ("python --version (or python3 --version)", True),
                    ("python install", False),
                    ("open python.py", False),
                    ("pip run python", False),
                ],
                "explanation": "The version flag confirms which interpreter the terminal can find.",
            },
            {
                "content": "Why does `python hello.py` sometimes fail even when the file exists?",
                "options": [
                    ("The terminal is in a different working directory", True),
                    ("Python cannot run files with text", False),
                    ("Comments disable the file", False),
                    ("The file must be named main.py", False),
                ],
                "explanation": "A relative filename is resolved against the terminal's current directory.",
            },
            {
                "content": "What is the REPL best suited for?",
                "options": [
                    ("Quick experiments and checking small expressions", True),
                    ("Storing a long program permanently", False),
                    ("Installing packages", False),
                    ("Compiling Python to machine code", False),
                ],
                "explanation": "The REPL is immediate and temporary; scripts are durable.",
            },
            {
                "content": "Which habit gives the strongest evidence that a change worked?",
                "options": [
                    ("Run the program and check a specific expected result", True),
                    ("Assume it works because the editor shows no red underline", False),
                    ("Change several unrelated lines together", False),
                    ("Rename the file", False),
                ],
                "explanation": "Verification means observing a concrete expected output, not hoping.",
            },
        ],
    },
    "projects": [],
}
