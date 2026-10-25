"""Module 8 — Functions."""

MODULE = {
    "slug": "functions-and-scope",
    "title": "Functions, Scope, and Recursion",
    "description": (
        "Turn long scripts into small, named, testable units. Learn parameters, "
        "return values, defaults, argument unpacking, scope, and when recursion "
        "is genuinely useful."
    ),
    "objectives": [
        "Define functions with clear inputs and outputs",
        "Choose between positional, keyword, default, and variadic parameters",
        "Explain local and global scope",
        "Write a safe recursive function with a base case",
    ],
    "estimated_duration_minutes": 115,
    "lessons": [
        {
            "slug": "functions-parameters-return-values",
            "title": "Functions, Parameters, and Return Values",
            "description": (
                "A function is a contract: give me these inputs, and I will give "
                "you this output. Learn to design that contract well."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "functions", "parameters", "return"],
            "objectives": [
                "Define and call functions",
                "Return values instead of printing as a side effect",
                "Use positional and keyword arguments",
                "Write docstrings and small functions",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Defining Functions",
                    "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Functions, Parameters, and Return Values

## From script to reusable unit

Without a function:

```python
price = 100
tax = 0.2
total = price * (1 + tax)
print(total)
```

With one:

```python
def total_with_tax(price, tax_rate):
    return price * (1 + tax_rate)


print(total_with_tax(100, 0.2))
```

The second version can be tested with many inputs. That is the real benefit: not fewer characters, but a unit you can trust and reuse.

## Return, do not print (inside the calculation)

```python
def bad_double(number):
    print(number * 2)


def good_double(number):
    return number * 2
```

`good_double(4)` gives a value that other code can store, compare, or combine. `bad_double` only writes to the screen; its result cannot be used.

Print at the edge of the program, not inside every helper.

## Parameter styles

```python
def greet(name, punctuation="!"):
    return f"Hello, {name}{punctuation}"


print(greet("Ada"))              # Hello, Ada!
print(greet("Ada", "?"))         # Hello, Ada?
print(greet(name="Ada", punctuation="."))  # keyword arguments
```

Default arguments make a function easier to call, but they must come after required parameters.

## *args and **kwargs

```python
def total(*numbers):
    return sum(numbers)


def label(**fields):
    return ", ".join(f"{key}={value}" for key, value in fields.items())


print(total(1, 2, 3))
print(label(level="beginner", topic="functions"))
```

Use these sparingly. A function that accepts anything is harder to understand and test than one with a clear signature.

## Docstrings

```python
def is_even(number):
    """Return True when number is divisible by 2."""
    return number % 2 == 0
```

A docstring states the contract in one sentence. If the function needs a paragraph of explanation, it may be doing too much.

## Common mistakes

- Printing inside a calculation instead of returning.
- Forgetting that `return` exits immediately.
- Using a mutable default argument (`def f(items=[]):`) and sharing state between calls.
- Reaching for `*args/**kwargs` when explicit parameters would be clearer.
- Giving functions vague names like `do_stuff`.

## Guided practice

Predict:

```python
def apply_twice(value, operation):
    return operation(operation(value))


print(apply_twice(3, lambda n: n + 5))
```

Expected output: `13`. The function receives another function as an argument — higher-order programming preview.

## Independent practice

Refactor a script that computes a shopping total into at least three functions: `line_total`, `subtotal`, and `apply_discount`. Each should return a value.

## Summary

Functions turn repeated work into named contracts. Clear parameters and returns make code testable; printing inside helpers hides their results. Keep signatures explicit unless flexibility is genuinely needed.

## Further reading

- [Python Tutorial — Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
''',
            "exercises": [
                {
                    "title": "Safe division function",
                    "description": "Write a clear contract with explicit failure.",
                    "instructions": (
                        "Complete safe_divide(a, b). Return a / b, or None when b is "
                        "zero. Do not print and do not raise for the zero case."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def safe_divide(a, b):\n    pass\n',
                    "solution": 'def safe_divide(a, b):\n    if b == 0:\n        return None\n    return a / b\n',
                    "tests": 'assert safe_divide(10, 2) == 5.0\nassert safe_divide(1, 0) is None\nassert safe_divide(-9, 3) == -3.0\n',
                    "hints": [
                        "Check the zero case before dividing.",
                        "Return None explicitly; do not rely on an implicit return.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "functions", "validation"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "scope-defaults-and-recursion",
            "title": "Scope, Defaults, and Recursion",
            "description": (
                "Understand where names live, avoid shared-default bugs, and use "
                "recursion only when the problem naturally decomposes."
            ),
            "difficulty": "intermediate",
            "minutes": 45,
            "tags": ["python", "scope", "recursion", "defaults"],
            "objectives": [
                "Explain local versus global names",
                "Avoid mutable default arguments",
                "Write a recursive function with a base case",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — More on Defining Functions",
                    "url": "https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions",
                    "resource_type": "reference",
                },
                {
                    "title": "Python FAQ — Mutable default arguments",
                    "url": "https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Scope, Defaults, and Recursion

## Scope is where a name is visible

```python
count = 0

def increment():
    count = 1
    return count

print(increment())  # 1
print(count)        # 0
```

Assignment inside the function creates a local name. Without `global`, the outer `count` is unchanged.

Reading a global is allowed:

```python
tax_rate = 0.2

def total(price):
    return price * (1 + tax_rate)
```

Avoid using `global` for state that could be passed in as a parameter. Explicit inputs are easier to test.

## The mutable default trap

```python
def add_item(item, items=[]):
    items.append(item)
    return items


print(add_item("a"))  # ['a']
print(add_item("b"))  # ['a', 'b']  ← surprising!
```

The default list is created once, when the function is defined. Use `None` as a sentinel:

```python
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

## Recursion

A recursive function calls itself on a smaller problem, with a base case that stops the chain.

```python
def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

```python
print(factorial(5))  # 120
```

### Why it works

- `factorial(5)` calls `factorial(4)`.
- Each call waits for the next, multiplying on the way back.
- `factorial(1)` returns `1` without recursing — the base case.

Every recursive function needs:

1. A base case.
2. Progress toward the base case.
3. A reason recursion is clearer than a loop.

Python limits recursion depth (usually around 1000). Deep recursion raises `RecursionError`; an iterative solution may be safer for large inputs.

## Common mistakes

- Missing base case → infinite recursion.
- Forgetting to return the recursive result.
- Mutating shared default data.
- Using `global` to avoid designing parameters.
- Assuming recursion is always faster; it often is not.

## Guided practice

Trace `factorial(3)` on paper. How many calls are active before the first return? Three.

## Independent practice

Write `sum_digits(n)` recursively: `sum_digits(1234)` should return `10`. Then write an iterative version and compare clarity.

## Summary

Names live in scopes; assignment creates locals unless you deliberately opt out. Defaults are evaluated once, so never use mutable defaults. Recursion is a precise tool with a base case and a shrinking problem.

## Further reading

- [Python FAQ — Default arguments](https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects)
- [Python reference — Execution model](https://docs.python.org/3/reference/executionmodel.html)
''',
            "exercises": [
                {
                    "title": "Recursive factorial",
                    "description": "Implement recursion with validation and a base case.",
                    "instructions": (
                        "Complete factorial(n) recursively. Return 1 for 0 and 1. "
                        "Raise ValueError for negative input."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def factorial(n):\n    pass\n',
                    "solution": 'def factorial(n):\n    if n < 0:\n        raise ValueError("n must be non-negative")\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n',
                    "tests": 'assert factorial(0) == 1\nassert factorial(5) == 120\nassert factorial(6) == 720\ntry:\n    factorial(-1)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\n',
                    "hints": [
                        "Handle negative input first.",
                        "The recursive call is n * factorial(n - 1).",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "recursion", "functions"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 8 Assessment — Functions",
        "description": "Check return values, scope, defaults, and recursion.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Why is returning a value usually better than printing inside a helper function?",
                "options": [
                    ("The caller can store, test, and reuse the result", True),
                    ("Return is faster than print", False),
                    ("Print does not work in functions", False),
                    ("It prevents all errors", False),
                ],
                "explanation": "Returning separates calculation from presentation and makes the function testable.",
            },
            {
                "content": "What is wrong with `def add(item, items=[]):`?",
                "options": [
                    ("The same list is shared across calls", True),
                    ("Lists cannot be parameters", False),
                    ("The function cannot return", False),
                    ("It needs a type annotation", False),
                ],
                "explanation": "Mutable defaults are evaluated once, so subsequent calls reuse the same object.",
            },
            {
                "content": "What does a recursive function need to stop?",
                "options": [
                    ("A base case and progress toward it", True),
                    ("A global variable", False),
                    ("A print statement", False),
                    ("A list", False),
                ],
                "explanation": "Without a base case, recursion continues until the interpreter's limit.",
            },
            {
                "content": "Which assignment creates a local variable inside a function?",
                "options": [("count = 1", True), ("count += 1 on a global without global", False), ("print(count)", False), ("return count", False)],
                "explanation": "A plain assignment binds a local name; reading an outer name is different.",
            },
        ],
    },
    "projects": [
        {
            "title": "Contact Book",
            "description": (
                "Build a menu-driven contact manager with search, validation, "
                "and JSON persistence."
            ),
            "requirements": (
                "1. Add, view, search, update, and delete contacts\n"
                "2. Validate names, phone numbers, and emails\n"
                "3. Persist contacts to a JSON file and reload on start\n"
                "4. Handle duplicate names and missing records clearly\n"
                "5. Split storage, validation, and menu code into functions"
            ),
            "difficulty": "medium",
            "hours": 5,
            "tags": ["Python", "Functions", "JSON", "Validation"],
            "starter_files": {
                "contacts.py": "import json\n\nDATA_FILE = \"contacts.json\"\n\n\ndef load_contacts(path=DATA_FILE):\n    try:\n        with open(path, encoding=\"utf-8\") as handle:\n            return json.load(handle)\n    except FileNotFoundError:\n        return []\n\n\n# TODO: implement add/search/update/delete and a menu loop\n"
            },
            "rubric": [
                {"criterion": "CRUD operations persist and reload correctly", "points": 30},
                {"criterion": "Bad input is rejected with helpful messages", "points": 25},
                {"criterion": "Storage, validation, and UI are separated", "points": 25},
                {"criterion": "Missing file, duplicate email, and empty search are handled", "points": 20},
            ],
        },
    ],
}
