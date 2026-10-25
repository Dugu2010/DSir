"""Module 1 — Programming foundations."""

MODULE = {
    "slug": "python-foundations",
    "title": "Programming Foundations",
    "description": (
        "Build the mental model first: what a program is, what Python does when "
        "it runs, how to work in the REPL and in files, and how to read errors "
        "without panicking."
    ),
    "objectives": [
        "Explain what a program, source code, execution, and output are",
        "Run Python interactively and from a .py file",
        "Use print() deliberately and predict output before running",
        "Read a simple traceback and make one small fix at a time",
    ],
    "estimated_duration_minutes": 90,
    "lessons": [
        {
            "slug": "what-is-python-and-how-programs-run",
            "title": "What Is Python, and How Does a Program Run?",
            "description": (
                "The core mental model: instructions, execution, output, the "
                "REPL, scripts, and your first experience of errors."
            ),
            "difficulty": "beginner",
            "minutes": 35,
            "tags": ["python", "programming-basics", "execution", "debugging"],
            "objectives": [
                "Explain what a program is in your own words",
                "Distinguish source code, execution, and output",
                "Run Python interactively and from a saved file",
            ],
            "preserve_content": True,
            "content": r'''# What Is Python, and How Does a Program Run?

A program is a set of instructions a computer can execute. Python is the language we use to write those instructions.

## Two ways to run Python

The **REPL** lets you type one instruction and see the result immediately:

```text
>>> print("Hello")
Hello
```

A **script** is a `.py` file you save and run again:

```python
print("My first Python file")
print("I am learning by running code")
```

```bash
python hello.py
```

## Code is not output

The code is what you wrote. The output is what appeared when Python ran it. Keeping those ideas separate is the beginning of real debugging skill.

## The habit that matters

Use this loop constantly:

**write → run → observe → change → run again**

Predict the output before you press Run. When a prediction is wrong, you have found a precise gap in your understanding — not evidence that you are bad at programming.

## Reading a first error

```python
print("Hello"
```

Python reports a syntax error because the parentheses do not match. Read the last line of the traceback, find the line number, inspect the code, change one thing, and run again.

## Read code out loud

A useful beginner exercise is to describe each line in plain language before running it:

```python
name = "Ada"                 # store the text Ada under the name "name"
print("Hello,", name)        # show the greeting followed by that text
```

This feels slow at first and then becomes automatic. Programmers who can explain a line usually debug it faster, because they notice when the explanation and the actual behaviour disagree.

## Comments are for the reader

```python
# Calculate the total price including 5% tax
price = 100
total = price * 1.05
```

The comment explains the intention. The code explains the mechanics. Do not comment every line; explain the parts a reader could misread.

## Summary

- Python is a programming language; the interpreter executes your code.
- The REPL is for quick experiments; scripts are for programs you keep.
- Source code, execution, and output are different things.
- Errors are information, not a verdict.
''',
            "resources": [
                {
                    "title": "Python.org — Getting Started",
                    "url": "https://www.python.org/about/gettingstarted/",
                    "resource_type": "reference",
                },
                {
                    "title": "Official Python Tutorial — Using the Python Interpreter",
                    "url": "https://docs.python.org/3/tutorial/interpreter.html",
                    "resource_type": "reference",
                },
            ],
            "exercises": [],
        },
        {
            "slug": "running-python-and-reading-errors",
            "title": "Running Python and Reading Your First Errors",
            "description": (
                "Turn the write-run-observe loop into a reliable habit. Learn "
                "where Python looks for files, what a traceback tells you, and "
                "how to fix one problem at a time."
            ),
            "difficulty": "beginner",
            "minutes": 30,
            "tags": ["python", "syntax", "traceback", "workflow"],
            "objectives": [
                "Create, save, and run a Python file",
                "Explain the three parts of a basic traceback",
                "Fix a small syntax error with a minimal edit",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Errors and Exceptions",
                    "url": "https://docs.python.org/3/tutorial/errors.html",
                    "resource_type": "reference",
                },
                {
                    "title": "MIT OCW 6.100L — Lecture 1",
                    "url": "https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Running Python and Reading Your First Errors

## What you are learning

Writing code is only half the loop. The other half is running it, observing the result, and making one deliberate change. This lesson makes that loop concrete.

**Prerequisites:** the previous lesson, or a basic idea of what `print()` does.

## The three ways beginners run Python

1. **An online notebook or DSir's playground** — fastest way to experiment.
2. **The REPL** — type `python` (or `python3`) in a terminal, then try expressions one at a time.
3. **A saved script** — create `hello.py`, write code, then run `python hello.py`.

All three execute Python. They differ in *where the code lives* and *how long it lasts*.

> A `.py` file is not magic. It is a text file that Python reads from top to bottom.

## Your first saved program

Create a file named `about_me.py`:

```python
print("Ada")
print("Learning Python")
print("Building a small calculator")
```

Run it:

```bash
python about_me.py
```

Expected output:

```text
Ada
Learning Python
Building a small calculator
```

### Why it works

- `print(...)` calls a built-in function.
- The text in quotes is a string.
- Each `print()` finishes with a newline, so three calls produce three lines.
- Python executes statements in order, top to bottom.

Change one line. Run again. That is the entire learning method: small change, immediate feedback.

## Reading a traceback

Suppose your file contains:

```python
print("Ready")
print("Go"
```

You will see something like:

```text
  File "about_me.py", line 2
    print("Go"
         ^
SyntaxError: '(' was never closed
```

Read it like a map:

- **File and line:** `about_me.py`, line 2.
- **The marker (`^`):** where Python noticed the problem.
- **The final message:** what kind of problem it is.

The fix is one character:

```python
print("Go")
```

Python reports the *first* problem it cannot get past. That is why fixing one error can reveal another. This is normal.

## Common mistakes

- **Running the wrong directory.** `python about_me.py` only works if the terminal is in the folder containing that file.
- **Using `Print` instead of `print`.** Python is case-sensitive.
- **Changing five lines at once.** You lose the ability to tell which change helped.
- **Treating the error message as a personal failure.** It is diagnostic data.

## Guided practice

Predict the output, then run it:

```python
print("one")
print("two")
print(1 + 2)
```

Expected output:

```text
one
two
3
```

Notice that `"1 + 2"` (with quotes) would print the characters, while `1 + 2` prints the result. We will study that distinction properly later.

### Hints

- Text in quotes is displayed literally.
- Arithmetic outside quotes is evaluated first.

## Independent practice

1. Write a script with four `print()` calls that introduces your learning goal.
2. Deliberately remove a closing parenthesis, run the file, and read the traceback out loud.
3. Fix it with one edit.

## Check yourself

- Can you explain the difference between the REPL and a script?
- Can you find the line number in a traceback?
- Do you change one thing before rerunning?

## Summary

A reliable workflow is more valuable than memorising syntax: write a small program, run it, read what happened, change one thing, and run it again.

## Further reading

- [Python Tutorial — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python.org — Getting Started](https://www.python.org/about/gettingstarted/)
''',
            "exercises": [
                {
                    "title": "Build a reusable greeting",
                    "description": "Practise functions, strings, and predicting output.",
                    "instructions": (
                        "Complete greeting(name) so it returns the text "
                        "'Hello, <name>!'. Then print the result of greeting('Ada')."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def greeting(name):\n    # Return the greeting text\n    pass\n\n\nprint(greeting("Ada"))\n',
                    "solution": 'def greeting(name):\n    return f"Hello, {name}!"\n\n\nprint(greeting("Ada"))\n',
                    "tests": 'assert greeting("Ada") == "Hello, Ada!"\nassert greeting("Sam") == "Hello, Sam!"\n',
                    "hints": [
                        "A function uses the return keyword to send a value back.",
                        "An f-string inserts a variable: f\"Hello, {name}!\".",
                    ],
                    "points": 10,
                    "minutes": 10,
                    "tags": ["python", "functions", "f-strings"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 1 Assessment — Programming Foundations",
        "description": "Check the mental model before adding language features.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What is the best description of a program?",
                "options": [
                    ("A set of instructions a computer can carry out", True),
                    ("The output shown after you press Run", False),
                    ("The programming language's logo", False),
                    ("A file extension", False),
                ],
                "explanation": "A program is executable instructions; output is one possible result of running it.",
            },
            {
                "content": "Which statement is true about the REPL?",
                "options": [
                    ("It evaluates one expression at a time and shows results immediately", True),
                    ("It permanently stores every program you type", False),
                    ("It only works with files ending in .repl", False),
                    ("It replaces the need to save scripts", False),
                ],
                "explanation": "The REPL is for quick interactive experiments; scripts are for reusable programs.",
            },
            {
                "content": "Why should you predict output before running code?",
                "options": [
                    ("A wrong prediction reveals a precise gap in understanding", True),
                    ("It makes Python run faster", False),
                    ("Python refuses to run otherwise", False),
                    ("It replaces the need to read errors", False),
                ],
                "explanation": "Prediction turns running code into an experiment with useful feedback.",
            },
            {
                "content": "What is the first practical step when Python reports a syntax error?",
                "options": [
                    ("Read the final message and inspect the indicated line", True),
                    ("Delete the whole file and start again", False),
                    ("Change every line to uppercase", False),
                    ("Ignore it and submit", False),
                ],
                "explanation": "Tracebacks point to the location and kind of problem; fix one thing, then run again.",
            },
            {
                "content": "What does `print(\"2 + 3\")` display?",
                "options": [("2 + 3", True), ("5", False), ("23", False), ("An error", False)],
                "explanation": "The quotes make it a string, so the characters are printed literally.",
            },
        ],
    },
    "projects": [],
}
