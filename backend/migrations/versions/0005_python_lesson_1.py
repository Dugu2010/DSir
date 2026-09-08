"""Add Python foundations lesson 1.

Revision ID: 0005_python_lesson_1
Revises: 0004_course_source_text
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_python_lesson_1"
down_revision: Union[str, None] = "0004_course_source_text"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COURSE_SLUG = "python"
MODULE_SLUG = "python-foundations"
LESSON_SLUG = "what-is-python-and-how-programs-run"

LESSON_MARKDOWN = r'''# What Is Python, and How Does a Program Run?

Welcome to Python.

Before we learn variables, loops, functions, or classes, we need one simple mental model: **a program is a set of instructions that a computer follows.**

Python is the language we will use to write those instructions.

This lesson is deliberately small in vocabulary but deep in understanding. By the end, you should be able to create a Python file, run it, predict what a simple program will do, recognize the difference between source code and output, and read a basic error without panicking.

## Learning objectives

By the end of this lesson, you can:

- Explain what a program is in your own words.
- Explain what Python is and what the Python interpreter does.
- Distinguish source code, execution, and output.
- Run Python code interactively and from a `.py` file.
- Use `print()` to display information.
- Read a simple traceback and identify that Python is telling you where and why execution failed.
- Make a tiny change, run the program again, and observe the result.

## 1. Start with the real problem: giving instructions

Imagine telling a person:

1. Open the calculator.
2. Add 10 and 5.
3. Show me the answer.

A computer also needs instructions, but computers are extremely literal. They do not fill in missing steps the way a human might.

A **program** is a collection of instructions written so that a computer can carry out a task.

Programming is therefore not primarily about memorizing commands. It is about learning how to express a solution precisely enough for a computer to execute it.

## 2. So what is Python?

**Python is a programming language.**

A programming language gives us rules and vocabulary for writing instructions that software can understand and execute.

Python is popular because its syntax is relatively readable, its standard library is extensive, and it is used in many areas: automation, web development, data work, testing, scientific computing, tooling, and AI.

You do not need to memorize that list. The important idea is:

> Python is the language in which we are going to express our programs.

## 3. Your first Python instruction

Try this:

```python
print("Hello, DSir!")
```

`print()` asks Python to display something.

The text inside the quotation marks is a **string literal**. We will study strings properly later; for now, think of it as a piece of text.

The result is:

```text
Hello, DSir!
```

Notice the difference:

**Code you wrote:**

```python
print("Hello, DSir!")
```

**Output produced by running it:**

```text
Hello, DSir!
```

The output is not the program. It is a result produced by executing the program.

## 4. What actually happens when you run Python?

At a beginner level, use this mental model:

**You write Python source code → Python runs/interprets it → the computer performs the requested operations → you observe results or an error.**

The exact implementation of Python is more sophisticated than this model, and later we will learn about parsing, bytecode, the Python virtual machine, implementations such as CPython, and execution details. You do not need those details yet.

For now, focus on the workflow:

**write → run → observe → change → run again**

This loop is one of the most important habits you will develop as a programmer.

## 5. Interactive Python: the REPL

If you start Python without giving it a script, you can normally enter expressions interactively.

For example:

```text
>>> print("Hello")
Hello
>>> print(2 + 3)
5
```

The `>>>` prompt means Python is waiting for your input.

This interactive environment is commonly called the **REPL**: Read, Evaluate, Print, Loop.

You type something, Python reads it, evaluates it, shows a result when appropriate, and waits for the next instruction.

The REPL is excellent for quick experiments.

## 6. Python files: scripts

For a real program, you will usually save your code in a file ending in `.py`.

Create a file called:

```text
hello.py
```

Put this inside:

```python
print("My first Python file")
print("I am learning by running code")
```

Then run the file using the Python command available on your system. A common command is:

```bash
python hello.py
```

On some systems, the command is:

```bash
python3 hello.py
```

Do not worry if your environment uses a different command. DSir will teach environment setup separately.

The important distinction is:

- **REPL:** experiment interactively.
- **Script:** save a program in a file so you can run it again.

## 7. Programs do not always succeed

Try deliberately making a small mistake:

```python
print("Hello"
```

Python cannot execute this because the parentheses do not match.

You will get an error message. The exact formatting can vary with the Python version and environment.

An error is not Python saying, "You are bad at programming."

It is information about a problem that prevented Python from doing what you asked.

### A useful beginner habit

When an error appears:

1. Read the **last line** first.
2. Look at the file and line number Python identifies.
3. Read the relevant code carefully.
4. Fix one thing.
5. Run the program again.

Do not randomly change five lines at once. You want to learn which change fixed the problem.

## 8. Code is precise

Compare:

```python
print("Hello")
```

with:

```python
Print("Hello")
```

These are not equivalent. Python is case-sensitive, so `print` and `Print` are different names.

This may feel unnecessarily strict at first. It is actually useful: programs need precise, unambiguous instructions.

## 9. Predict before you run

One of the best ways to learn programming is to stop treating the computer as a slot machine.

Before pressing Run, ask:

> What do I think this program will do?

For example:

```python
print("A")
print("B")
```

Predict the output before running it.

Then run it.

If your prediction was wrong, that is useful. You have found something about how the language behaves that you did not yet understand.

## 10. A tiny experiment

Change the program to:

```python
print("Python")
print("is")
print("fun")
```

Now change it again:

```python
print("Python is fun")
```

Both programs display similar words, but they are different programs. You are already practicing an important programming skill: changing instructions and observing consequences.

## Common beginner mistakes

### Mistake 1: Confusing code with output

`print("Hello")` is an instruction.

`Hello` is the resulting output.

### Mistake 2: Thinking errors mean the whole program is ruined

Most programming errors are local problems you can investigate and fix.

### Mistake 3: Copying code without predicting it

Copying can get a program running, but prediction and experimentation build understanding.

### Mistake 4: Changing many things at once

Make one small change, run again, and observe.

## Practice: predict the output

Do not run these until you have made a prediction.

### Example A

```python
print("DSir")
print("Python")
```

### Example B

```python
print(10)
print(20)
```

### Example C

```python
print("10")
print("20")
```

Notice that Examples B and C look similar but are not using the same kind of value. We will formally learn the difference later.

## Exercises

### Exercise 1 — Your first program

Create a Python file that prints:

```text
My name is <your name>
I am learning Python
I will build things with it
```

**Goal:** practice creating and running a `.py` file.

### Exercise 2 — Predict first

Without running it, write down the exact output:

```python
print("One")
print("Two")
print("Three")
```

Then run it and compare.

### Exercise 3 — Debug it

This program contains an error:

```python
print("Python is"
print("awesome")
```

Find and fix the problem.

### Exercise 4 — Experiment

Write a program containing five `print()` statements. Change the text, order the statements differently, run it, and explain what changed in the output.

## Challenge

Create a tiny **DSir introduction program** that produces at least five lines of output.

Rules:

- Use only `print()` for now.
- Do not use variables, loops, functions, imports, or other concepts that have not been taught.
- Make the output meaningful rather than five random words.

## Knowledge check

1. What is a program?
2. What is Python?
3. What is the difference between source code and output?
4. What is the REPL useful for?
5. What does a `.py` file normally contain?
6. What should you do when Python reports an error?
7. Why are `print` and `Print` different?

## Mastery criteria

You are ready to move on when you can independently:

- Create and run a `.py` file.
- Explain what Python is without memorizing a definition.
- Explain the write → run → observe cycle.
- Use `print()` correctly for simple output.
- Predict the output of a short sequence of `print()` calls.
- Find and fix the missing parenthesis in a simple program.
- Read a basic Python error without immediately giving up.

## Summary

You have learned the first programming workflow:

**Write code → run it → observe the result → investigate errors → change the code → run again.**

Python is the language we will use to express our instructions. A `.py` file stores Python source code, and running that code causes Python to execute it and produce output or report an error.

That is enough for lesson one.

Next, we will start learning how Python represents and works with **values**—the foundation for everything from simple scripts to large applications.
'''


def upgrade() -> None:
    # Intentionally data-only: resolve existing course/module rows and insert one lesson.
    bind = op.get_bind()

    course = bind.execute(
        sa.text("SELECT id FROM courses WHERE slug = :slug AND deleted_at IS NULL LIMIT 1"),
        {"slug": COURSE_SLUG},
    ).fetchone()
    if course is None:
        raise RuntimeError("Cannot seed Python lesson: course with slug 'python' does not exist")

    module = bind.execute(
        sa.text("SELECT id FROM modules WHERE course_id = :course_id AND slug = :slug AND deleted_at IS NULL LIMIT 1"),
        {"course_id": course[0], "slug": MODULE_SLUG},
    ).fetchone()
    if module is None:
        raise RuntimeError("Cannot seed Python lesson: module 'python-foundations' does not exist")

    existing = bind.execute(
        sa.text("SELECT id FROM lessons WHERE module_id = :module_id AND slug = :slug LIMIT 1"),
        {"module_id": module[0], "slug": LESSON_SLUG},
    ).fetchone()
    if existing is not None:
        return

    lesson_id = bind.execute(
        sa.text("""
            INSERT INTO lessons (
                module_id, title, slug, description, content, content_markdown,
                learning_objectives, difficulty, estimated_duration_minutes,
                display_order, skill_tags, is_free_preview, version, status,
                published_at, created_at, updated_at
            ) VALUES (
                :module_id, :title, :slug, :description, :content, :content_markdown,
                CAST(:learning_objectives AS jsonb), :difficulty, :duration,
                :display_order, CAST(:skill_tags AS text[]), :preview, 1, 'published',
                now(), now(), now()
            ) RETURNING id
        """),
        {
            "module_id": module[0],
            "title": "What Is Python, and How Does a Program Run?",
            "slug": LESSON_SLUG,
            "description": "Build the correct mental model for programs, Python, execution, the REPL, scripts, output, and beginner-friendly error handling.",
            "content": LESSON_MARKDOWN,
            "content_markdown": LESSON_MARKDOWN,
            "learning_objectives": '["Explain what a program is","Explain what Python and the Python interpreter do","Run a Python script","Use print() for simple output","Distinguish source code from output","Recognize and investigate basic errors"]',
            "difficulty": "beginner",
            "duration": 35,
            "display_order": 1,
            "skill_tags": "{python,programming-basics,execution,debugging}",
            "preview": True,
        },
    ).scalar_one()

    # Keep the module's cached lesson count accurate if the column exists (it does in the DSir schema).
    bind.execute(
        sa.text("UPDATE modules SET lesson_count = (SELECT count(*) FROM lessons WHERE module_id = :module_id AND deleted_at IS NULL) WHERE id = :module_id"),
        {"module_id": module[0]},
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM lessons WHERE slug = :slug AND module_id IN (SELECT id FROM modules WHERE slug = :module_slug)"),
        {"slug": LESSON_SLUG, "module_slug": MODULE_SLUG},
    )
