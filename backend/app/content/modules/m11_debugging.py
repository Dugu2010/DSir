"""Module 11 — Debugging and Pythonic iteration."""

MODULE = {
    "slug": "debugging-and-iterators",
    "title": "Debugging, Comprehensions, and Generators",
    "description": (
        "Debug with evidence instead of guesses, then use comprehensions, "
        "iterators, and generators to express data transformations clearly."
    ),
    "objectives": [
        "Read tracebacks and reproduce bugs reliably",
        "Use print, breakpoints, and assertions as debugging tools",
        "Write list, set, and dictionary comprehensions",
        "Explain lazy iteration and write a generator",
    ],
    "estimated_duration_minutes": 110,
    "lessons": [
        {
            "slug": "debugging-methodically",
            "title": "Debugging Methodically",
            "description": (
                "A repeatable process for finding bugs: reproduce, isolate, "
                "inspect state, form a hypothesis, and verify the fix."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "debugging", "tracebacks", "assertions"],
            "objectives": [
                "Reproduce a bug with a minimal input",
                "Read a traceback from the last line upward",
                "Use assertions and breakpoints to inspect assumptions",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Errors and Exceptions",
                    "url": "https://docs.python.org/3/tutorial/errors.html",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — pdb",
                    "url": "https://docs.python.org/3/library/pdb.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Debugging Methodically

## A bug is a claim about reality that failed

Debugging is not staring at code until inspiration arrives. Use a loop:

1. **Reproduce** the failure with the smallest input you can find.
2. **Locate** the first point where reality diverges from your expectation.
3. **Inspect** the values at that point.
4. **Hypothesise** a cause.
5. **Change one thing** and verify.

## Read the traceback from the bottom

```python
def average(numbers):
    return sum(numbers) / len(numbers)


print(average([]))
```

```text
Traceback (most recent call last):
  File "demo.py", line 5, in <module>
    print(average([]))
  File "demo.py", line 2, in average
    return sum(numbers) / len(numbers)
ZeroDivisionError: division by zero
```

The last line names the failure. Just above it is the exact line in your code. Note the call chain: `average` was called with an empty list. The bug is not “Python is broken”; the function's contract did not cover empty input.

Decide the intended behaviour, then implement it:

```python
def average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

Returning `0` may or may not be right for your domain. Debugging often becomes a requirements question.

## Print with labels

```python
print("numbers:", numbers)
print("count:", len(numbers))
print("total:", sum(numbers))
```

Bare `print(x)` is ambiguous once several values are involved. Label the output. Remove debugging prints before committing.

## Assertions express assumptions

```python
def apply_discount(price, percent):
    assert 0 <= percent <= 100, "percent must be between 0 and 100"
    return price * (1 - percent / 100)
```

Assertions are for programmer errors and internal invariants, not user validation. They can be disabled with `python -O`.

## Breakpoints

```python
def calculate(items):
    total = 0
    for item in items:
        breakpoint()   # Python 3.7+
        total += item
    return total
```

At the `(Pdb)` prompt: `p total`, `p item`, `n` for next, `c` to continue, `q` to quit. In an editor, click the gutter to set a breakpoint instead.

## Isolate with a minimal reproduction

If a 200-line program fails, copy the smallest piece that still fails into a new file. The act of isolating often reveals the cause before you finish.

## Common mistakes

- Changing several things at once.
- Adding prints without labels.
- Fixing the symptom (catching the exception) instead of the cause.
- Assuming the bug is where the traceback points when the bad value was created earlier.
- Not re-running the original failing case after the fix.

## Guided practice

This function should return the largest number but fails for `[-5, -2, -9]`:

```python
def largest(numbers):
    best = 0
    for number in numbers:
        if number > best:
            best = number
    return best
```

Trace it. `best = 0` is wrong for all-negative input. Initialise from the first item or use `max()` after deciding how empty input should behave.

## Independent practice

Write a failing case for `parse_age` that returns `None` for `"0"` but should accept it. Then fix the function and add the case as a test.

## Summary

Debugging is a controlled experiment. Reproduce, locate, inspect, hypothesise, change one thing, and verify. Assertions and breakpoints are tools for checking assumptions, not decoration.

## Further reading

- [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- [pdb — The Python Debugger](https://docs.python.org/3/library/pdb.html)
''',
            "exercises": [
                {
                    "title": "Fix the average bug",
                    "description": "Handle empty input without dividing by zero.",
                    "instructions": (
                        "Fix average(numbers) so it returns 0 for an empty list and "
                        "the arithmetic mean otherwise."
                    ),
                    "type": "bug_fixing",
                    "difficulty": "easy",
                    "starter": 'def average(numbers):\n    return sum(numbers) / len(numbers)\n',
                    "solution": 'def average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)\n',
                    "tests": 'assert average([]) == 0\nassert average([2, 4, 6]) == 4\nassert average([5]) == 5\n',
                    "hints": [
                        "Check the empty case before dividing.",
                        "len([]) is 0, so division raises ZeroDivisionError.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "debugging", "functions"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "comprehensions-iterators-generators",
            "title": "Comprehensions, Iterators, and Generators",
            "description": (
                "Express transformations without boilerplate, and understand why "
                "generators can process data that would not fit in memory."
            ),
            "difficulty": "intermediate",
            "minutes": 45,
            "tags": ["python", "comprehensions", "iterators", "generators"],
            "objectives": [
                "Write list, set, and dictionary comprehensions",
                "Explain iterable versus iterator",
                "Write a generator function with yield",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — List Comprehensions",
                    "url": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions",
                    "resource_type": "reference",
                },
                {
                    "title": "Python Tutorial — Generators",
                    "url": "https://docs.python.org/3/tutorial/classes.html#generators",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Comprehensions, Iterators, and Generators

## Comprehensions are a notation for map/filter

```python
numbers = [1, 2, 3, 4, 5, 6]
squares = [n ** 2 for n in numbers]
evens = [n for n in numbers if n % 2 == 0]
lookup = {n: n ** 2 for n in numbers}
unique_lengths = {len(word) for word in ["a", "bb", "cc"]}
```

Read a list comprehension as: “build a list of `expression` for each `item` in `iterable`, optionally where `condition`.”

Use comprehensions when the transformation fits on one readable line. A nested three-level comprehension with side effects is worse than a loop.

## Comprehensions evaluate eagerly

`squares = [n ** 2 for n in numbers]` builds the whole list. For a million items, that is a million integers in memory.

A generator expression uses parentheses:

```python
squares = (n ** 2 for n in numbers)
print(next(squares))   # 1
print(next(squares))   # 4
```

The values are produced on demand.

## Iterables and iterators

- An **iterable** can produce an iterator (`list`, `str`, `dict`, file objects).
- An **iterator** produces values one at a time and remembers its position.

```python
values = [10, 20, 30]
iterator = iter(values)
print(next(iterator))  # 10
print(next(iterator))  # 20
```

Once an iterator is exhausted, it stays exhausted.

## Generators

A function containing `yield` returns a generator:

```python
def read_in_chunks(text, size=3):
    for start in range(0, len(text), size):
        yield text[start:start + size]


for chunk in read_in_chunks("abcdefgh"):
    print(chunk)
```

```text
abc
def
gh
```

The function pauses at each `yield` and resumes when the next value is requested. This is how large files and streams can be processed without loading everything at once.

## Generator pipeline

```python
def positive(numbers):
    for number in numbers:
        if number > 0:
            yield number


values = [-2, 0, 3, 5]
print(sum(positive(values)))  # 8
```

Pipelines compose lazily: each stage pulls only what the next stage needs.

## Common mistakes

- Using a comprehension for side effects (`[print(x) for x in values]`) — use a loop.
- Reusing an exhausted iterator.
- Assuming a generator can be indexed or measured with `len()`.
- Building a huge list when a generator would do.
- Overusing comprehensions until they are unreadable.

## Guided practice

Predict:

```python
values = [1, 2, 3]
gen = (x * 10 for x in values)
print(list(gen))
print(list(gen))
```

Expected `[10, 20, 30]` and `[]`. The second `list(gen)` consumes an exhausted iterator.

## Independent practice

Write `even_squares(limit)` as a generator yielding squares of even numbers below `limit`. Then write the list-comprehension version and explain the memory trade-off.

## Summary

Comprehensions are concise transformations. Generators produce values lazily and can handle streams too large for memory. Understand exhaustion and choose eagerly versus lazily on purpose.

## Further reading

- [List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Generators](https://docs.python.org/3/tutorial/classes.html#generators)
- [Iterator protocol](https://docs.python.org/3/library/stdtypes.html#iterator-types)
''',
            "exercises": [
                {
                    "title": "Even squares generator",
                    "description": "Write a lazy generator and consume it.",
                    "instructions": (
                        "Complete even_squares(limit) as a generator yielding the "
                        "squares of even numbers from 0 up to but not including limit."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def even_squares(limit):\n    pass\n',
                    "solution": 'def even_squares(limit):\n    for number in range(0, limit, 2):\n        yield number * number\n',
                    "tests": 'assert list(even_squares(10)) == [0, 4, 16, 36, 64]\nassert list(even_squares(1)) == [0]\nassert list(even_squares(0)) == []\n',
                    "hints": [
                        "range(0, limit, 2) produces even numbers.",
                        "Use yield, not return, to make a generator.",
                    ],
                    "points": 12,
                    "minutes": 10,
                    "tags": ["python", "generators", "comprehensions"],
                },
                {
                    "title": "Filter and transform names",
                    "description": "Use a comprehension with a condition.",
                    "instructions": (
                        "Complete long_names(names) returning title-cased names "
                        "of at least 3 characters, preserving order."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def long_names(names):\n    pass\n',
                    "solution": 'def long_names(names):\n    return [name.strip().title() for name in names if len(name.strip()) >= 3]\n',
                    "tests": 'assert long_names(["ada", "li", "grace", "alan"]) == ["Ada", "Grace", "Alan"]\nassert long_names([" ", "ab"]) == []\n',
                    "hints": [
                        "The condition goes after the for clause.",
                        "strip before checking length.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "comprehensions", "strings"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 11 Assessment — Debugging and Iteration",
        "description": "Check traceback reading, comprehensions, and lazy evaluation.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Where should you look first in a traceback?",
                "options": [
                    ("The final line, which names the exception", True),
                    ("The first line of the file", False),
                    ("The middle of the stack", False),
                    ("The terminal prompt", False),
                ],
                "explanation": "The exception type and message appear at the bottom; the frames above show the path.",
            },
            {
                "content": "What is the main advantage of a generator over a list comprehension?",
                "options": [
                    ("It produces values lazily and can use less memory", True),
                    ("It is always faster for small data", False),
                    ("It preserves duplicates", False),
                    ("It can be indexed", False),
                ],
                "explanation": "Generators yield on demand instead of materialising all results.",
            },
            {
                "content": "What happens after a generator is exhausted?",
                "options": [
                    ("Further iteration yields nothing", True),
                    ("It restarts automatically", False),
                    ("It raises ValueError", False),
                    ("It returns to the first yield", False),
                ],
                "explanation": "Generators are one-shot iterators.",
            },
            {
                "content": "Which comprehension builds a dictionary?",
                "options": [
                    ("{word: len(word) for word in words}", True),
                    ("[word: len(word) for word in words]", False),
                    ("(word: len(word) for word in words)", False),
                    ("{word, len(word) for word in words}", False),
                ],
                "explanation": "Curly braces with key: value produce a dictionary comprehension.",
            },
        ],
    },
    "projects": [
        {
            "title": "Text Analyzer",
            "description": (
                "Analyse a text file and report word frequencies, readability "
                "signals, and the most common terms."
            ),
            "requirements": (
                "1. Read a UTF-8 text file safely\n"
                "2. Count words, sentences, and unique terms\n"
                "3. Show the top 10 words and longest sentences\n"
                "4. Ignore common stop words\n"
                "5. Export a short Markdown report"
            ),
            "difficulty": "medium",
            "hours": 4,
            "tags": ["Python", "Files", "Dictionaries", "Comprehensions"],
            "starter_files": {
                "analyze.py": "from collections import Counter\n\nSTOP_WORDS = {\"the\", \"a\", \"an\", \"and\", \"or\", \"to\", \"of\", \"in\"}\n\n\ndef analyse(text):\n    # TODO: return counts and top terms\n    pass\n"
            },
            "rubric": [
                {"criterion": "Counts match the source text", "points": 30},
                {"criterion": "Empty files and punctuation are handled", "points": 25},
                {"criterion": "The report is easy to scan", "points": 20},
                {"criterion": "Analysis is separated from file I/O and formatting", "points": 25},
            ],
        },
    ],
}
