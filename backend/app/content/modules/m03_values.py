"""Module 3 — Values, variables, input, output, and conversion."""

MODULE = {
    "slug": "values-variables-input",
    "title": "Variables, Types, and Input",
    "description": (
        "Give values names, understand Python's core data types, and build "
        "interactive programs that convert and validate user input."
    ),
    "objectives": [
        "Create and reassign variables using clear names",
        "Identify int, float, str, bool, and None values",
        "Read input and convert it to the type you need",
        "Format readable output with f-strings",
    ],
    "estimated_duration_minutes": 95,
    "lessons": [
        {
            "slug": "variables-and-core-types",
            "title": "Variables and Python's Core Data Types",
            "description": (
                "Names point to values. Learn int, float, str, bool, None, and "
                "how Python's dynamic typing actually behaves."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "variables", "types", "strings"],
            "objectives": [
                "Assign and update variables",
                "Use type() to inspect a value",
                "Predict the result of mixing numeric types",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — An Informal Introduction to Python",
                    "url": "https://docs.python.org/3/tutorial/introduction.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Variables and Python's Core Data Types

## A variable is a name for a value

```python
name = "Ada"
age = 36
height = 1.68
is_learning = True
```

Read `=` as **“is assigned”**, not “equals”. The value on the right is created, then the name on the left points to it.

```python
age = age + 1
```

This creates a new integer and rebinds `age`. The original value is unchanged; no other name is affected.

## The types you will use constantly

| Type | Example | Used for |
|---|---|---|
| `int` | `42`, `-7` | whole numbers |
| `float` | `3.14`, `0.5` | decimals |
| `str` | `"hello"` | text |
| `bool` | `True`, `False` | yes/no decisions |
| `None` | `None` | “no value yet” |

The table is orientation, not memorisation homework. You will recognise each type by using it.

```python
print(type(42))
print(type(3.14))
print(type("42"))
print(type(True))
print(type(None))
```

Expected output:

```text
<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>
<class 'NoneType'>
```

Note `type("42")` is `str`. Quotes matter.

## Dynamic typing

Python does not require you to declare a type:

```python
value = 10       # int
value = "ten"    # now a str
```

This is flexible, not free. A variable's type can change, so code must still be designed around the values it expects. Later, type hints will document those expectations.

## Choosing names

```python
student_count = 24          # clear
seconds_per_day = 86400     # clear
x = 24                      # unclear outside a tiny scope
```

Rules: start with a letter or underscore, use letters/digits/underscores, avoid Python keywords, and remember that names are case-sensitive.

## f-strings

```python
name = "Ada"
score = 92.5
print(f"{name} scored {score:.1f}%")
```

```text
Ada scored 92.5%
```

The `:.1f` format spec keeps one decimal place. We will use formatting often because readable output is part of usable software.

## Common mistakes

- Confusing `"10"` with `10`; one is text, the other is a number.
- Naming a variable `class`, `for`, or `list` (keywords or built-ins you would shadow).
- Assuming `=` compares values. Comparison uses `==`.
- Reusing one-letter names everywhere until the code becomes unreadable.

## Guided practice

Predict the output before running:

```python
points = 10
points = points + 5
print(points)
print(type(points))
print(points == 15)
```

Expected output:

```text
15
<class 'int'>
True
```

### Why it works

1. `points` starts at `10`.
2. `points + 5` evaluates to `15`.
3. The name is rebound to `15`.
4. `==` compares; it does not assign.

## Independent practice

Create variables for a product name, unit price, quantity, and whether it is in stock. Print one sentence and one total-price line using f-strings.

## Summary

Variables name values. Types describe those values. Python is flexible about reassignment, so clarity in naming and formatting is your responsibility.

## Further reading

- [Python Tutorial — Informal Introduction](https://docs.python.org/3/tutorial/introduction.html)
- [Built-in Types](https://docs.python.org/3/library/stdtypes.html)
''',
            "exercises": [
                {
                    "title": "Compute body mass index",
                    "description": "Combine variables, arithmetic, and rounding.",
                    "instructions": (
                        "Complete bmi(weight_kg, height_m) so it returns BMI "
                        "rounded to two decimal places. BMI = weight / height²."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def bmi(weight_kg, height_m):\n    # Calculate and round to 2 decimals\n    pass\n',
                    "solution": 'def bmi(weight_kg, height_m):\n    return round(weight_kg / (height_m ** 2), 2)\n',
                    "tests": 'assert bmi(70, 1.75) == 22.86\nassert bmi(60, 1.5) == 26.67\n',
                    "hints": [
                        "Square a value with ** 2.",
                        "round(value, 2) keeps two decimal places.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "variables", "arithmetic"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "input-output-and-conversion",
            "title": "Input, Output, and Type Conversion",
            "description": (
                "Build interactive programs, convert strings to numbers safely, "
                "and handle the input that always breaks naive code."
            ),
            "difficulty": "beginner",
            "minutes": 35,
            "tags": ["python", "input", "conversion", "validation"],
            "objectives": [
                "Read a line of input with input()",
                "Convert between str, int, and float",
                "Handle invalid input without crashing",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Input and Output",
                    "url": "https://docs.python.org/3/tutorial/inputoutput.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Input, Output, and Type Conversion

## input() always returns a string

```python
name = input("What is your name? ")
print(f"Hello, {name}!")
```

If the user types `Ada`, `name` is the **string** `"Ada"`. That is true even if they type digits.

```python
age = input("Your age: ")
print(type(age))
```

Typing `36` prints `<class 'str'>`. Forgetting this produces one of the most common beginner errors:

```python
age = input("Your age: ")
print(age + 1)
```

```text
TypeError: can only concatenate str (not "int") to str
```

The message is accurate: `age` is text, and adding text to a number is undefined.

## Convert deliberately

```python
age = int(input("Your age: "))
print(age + 1)
```

`int("36")` produces the number `36`. Other useful conversions:

```python
float("2.5")     # 2.5
str(42)          # "42"
bool(0)          # False
bool("0")        # True  ← surprising!
```

`bool("0")` is `True` because a non-empty string is truthy. Type conversion rules are literal, not intuitive. Check them when they matter.

## Handle bad input

```python
raw = input("How many minutes? ")
try:
    minutes = int(raw)
except ValueError:
    print("Please enter a whole number.")
else:
    print(f"You planned {minutes} minutes.")
```

This is a small, complete validation flow. We will study exceptions properly later; for now, recognise the shape: **attempt → catch a specific failure → give a useful message.**

## A useful program pattern

```python
def parse_quantity(raw):
    try:
        quantity = int(raw)
    except ValueError:
        return None
    if quantity <= 0:
        return None
    return quantity


for text in ["3", "0", "many"]:
    print(text, "->", parse_quantity(text))
```

Expected output:

```text
3 -> 3
0 -> None
many -> None
```

Returning `None` keeps the parsing logic testable. Printing inside the function would make it harder to reuse.

## Common mistakes

- Adding input directly to a number without converting.
- Converting with `int("2.5")` (raises `ValueError`; use `float` first if decimals are allowed).
- Accepting negative quantities as valid.
- Catching every exception and hiding the real problem.

## Guided practice

Predict each result, then verify:

```python
print(int("7") + 3)
print("7" + "3")
print(float("7") + 0.5)
```

Expected output:

```text
10
73
7.5
```

### Hints

- Quotes mean concatenation for strings.
- `float` accepts decimal text.

## Independent practice

Write a program that asks for a price and a quantity, validates both, and prints the total or a clear error. Test it with `2.5` and `3`, then with `abc`.

## Summary

`input()` hands you text. Convert it explicitly, validate it deliberately, and design functions that return a clear success or failure value.

## Further reading

- [Python Tutorial — Input and Output](https://docs.python.org/3/tutorial/inputoutput.html)
- [Built-in Functions — input, int, float](https://docs.python.org/3/library/functions.html)
''',
            "exercises": [
                {
                    "title": "Safe integer parser",
                    "description": "Validate user-style text without raising errors.",
                    "instructions": (
                        "Complete parse_positive_int(text). Return the integer for "
                        "positive whole numbers; return None otherwise."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def parse_positive_int(text):\n    # Return a positive int or None\n    pass\n',
                    "solution": 'def parse_positive_int(text):\n    try:\n        value = int(text)\n    except (TypeError, ValueError):\n        return None\n    if value <= 0:\n        return None\n    return value\n',
                    "tests": 'assert parse_positive_int("12") == 12\nassert parse_positive_int("0") is None\nassert parse_positive_int("-4") is None\nassert parse_positive_int("abc") is None\nassert parse_positive_int("3.5") is None\n',
                    "hints": [
                        "int(\"3.5\") raises ValueError.",
                        "Catch ValueError and TypeError, then check the range.",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "validation", "exceptions"],
                },
                {
                    "title": "Format a receipt line",
                    "description": "Practice f-strings and numeric formatting.",
                    "instructions": (
                        "Complete receipt_line(name, price, quantity) so it returns "
                        "text like 'Coffee x2 = 9.00'. Use exactly two decimals."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def receipt_line(name, price, quantity):\n    pass\n',
                    "solution": 'def receipt_line(name, price, quantity):\n    return f"{name} x{quantity} = {price * quantity:.2f}"\n',
                    "tests": 'assert receipt_line("Coffee", 4.5, 2) == "Coffee x2 = 9.00"\nassert receipt_line("Tea", 2, 1) == "Tea x1 = 2.00"\n',
                    "hints": [
                        "Multiply price by quantity inside the f-string.",
                        "Use :.2f for two decimal places.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "f-strings", "numbers"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 3 Assessment — Variables and Input",
        "description": "Check your understanding of values, types, and conversion.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What is the type of the value returned by input()?",
                "options": [("str", True), ("int", False), ("float", False), ("bool", False)],
                "explanation": "input() always returns text; convert it explicitly when you need a number.",
            },
            {
                "content": "What does `print(\"7\" + \"3\")` output?",
                "options": [("73", True), ("10", False), ("An error", False), ("'73'", False)],
                "explanation": "Two strings are concatenated, producing the characters 73.",
            },
            {
                "content": "Which conversion would fail for the text \"3.5\"?",
                "options": [("int(\"3.5\")", True), ("float(\"3.5\")", False), ("str(\"3.5\")", False), ("bool(\"3.5\")", False)],
                "explanation": "int() does not truncate decimal text; use float() when decimals are valid.",
            },
            {
                "content": "Why is returning None often better than printing an error inside a parser?",
                "options": [
                    ("The caller can decide how to respond and the function stays testable", True),
                    ("None is faster than text", False),
                    ("It prevents all bugs", False),
                    ("Python requires it", False),
                ],
                "explanation": "Separating parsing from presentation makes reuse and testing much easier.",
            },
        ],
    },
    "projects": [],
}
