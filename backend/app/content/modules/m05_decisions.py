"""Module 5 — Decisions and logical thinking."""

MODULE = {
    "slug": "decisions",
    "title": "Conditional Statements and Logical Thinking",
    "description": (
        "Make programs choose between paths, validate input, and avoid the "
        "nested-ifs tangle that makes beginner code hard to reason about."
    ),
    "objectives": [
        "Write if/elif/else chains with correct indentation",
        "Use truthiness deliberately",
        "Structure validation so each rule is readable and testable",
        "Recognise when a lookup or early return is clearer than deep nesting",
    ],
    "estimated_duration_minutes": 95,
    "lessons": [
        {
            "slug": "if-elif-else",
            "title": "if, elif, and else",
            "description": (
                "Control flow is not about memorising syntax; it is about making "
                "the possible paths through a program obvious."
            ),
            "difficulty": "beginner",
            "minutes": 35,
            "tags": ["python", "conditionals", "control-flow"],
            "objectives": [
                "Write a valid if/elif/else chain",
                "Explain why order matters in elif chains",
                "Use early returns to reduce nesting",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — if Statements",
                    "url": "https://docs.python.org/3/tutorial/controlflow.html#if-statements",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# if, elif, and else

## The shape

```python
score = 82

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("Needs practice")
```

```text
B
```

The colon begins a block. The indented lines belong to that branch. Python uses indentation as syntax, not decoration.

## Only one branch runs

An `if/elif/else` chain stops after the first true condition. That is why order matters:

```python
score = 95

if score >= 70:
    print("pass")
elif score >= 90:
    print("excellent")
```

This prints `pass`, because the first condition already matched. Put the most specific or highest-priority condition first.

## Early returns flatten code

Nested code is hard to read:

```python
def shipping_cost(total, member):
    if total > 0:
        if member:
            return 0
        else:
            return 5
    else:
        return None
```

A flatter version says what it means:

```python
def shipping_cost(total, member):
    if total <= 0:
        return None
    if member:
        return 0
    return 5
```

Early returns work well when the invalid or simplest case can leave immediately.

## Validation rules

```python
def valid_username(name):
    if not name:
        return False
    if len(name) < 3:
        return False
    if " " in name:
        return False
    return True
```

Each rule is visible and testable. When one rule changes, you know where to edit.

## Common mistakes

- Mixing tabs and spaces.
- Writing `if x = 5:` instead of `if x == 5:`.
- Forgetting that only the first matching branch executes.
- Combining unrelated rules into one unreadable condition.
- Using `elif` when a new independent `if` is actually intended.

## Guided practice

Predict the outputs:

```python
temperature = 18
if temperature > 25:
    print("hot")
elif temperature > 15:
    print("mild")
else:
    print("cold")
```

```python
x = 10
if x > 5:
    print("A")
if x > 8:
    print("B")
```

The first prints `mild`. The second prints both `A` and `B` because the `if`s are independent.

### Hints

- `elif` belongs to the same chain.
- Separate `if` statements each evaluate.

## Independent practice

Write `ticket_price(age, is_student)` returning 0 for under 5, 8 for students, 12 otherwise. Handle invalid negative ages explicitly.

## Summary

Conditional chains choose one path. Order and indentation are meaningful. Prefer early returns and small validation functions over deep nesting.

## Further reading

- [Python Tutorial — if Statements](https://docs.python.org/3/tutorial/controlflow.html#if-statements)
''',
            "exercises": [
                {
                    "title": "Grade calculator",
                    "description": "Implement an ordered conditional chain.",
                    "instructions": (
                        "Complete grade(score) returning 'A' for 90+, 'B' for 80+, "
                        "'C' for 70+, 'D' for 60+, and 'F' otherwise. Invalid "
                        "scores below 0 or above 100 return 'invalid'."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def grade(score):\n    pass\n',
                    "solution": 'def grade(score):\n    if score < 0 or score > 100:\n        return "invalid"\n    if score >= 90:\n        return "A"\n    if score >= 80:\n        return "B"\n    if score >= 70:\n        return "C"\n    if score >= 60:\n        return "D"\n    return "F"\n',
                    "tests": 'assert grade(95) == "A"\nassert grade(80) == "B"\nassert grade(70) == "C"\nassert grade(0) == "F"\nassert grade(101) == "invalid"\n',
                    "hints": [
                        "Validate the range first.",
                        "Because each branch returns, you do not need elif.",
                    ],
                    "points": 10,
                    "minutes": 10,
                    "tags": ["python", "conditionals"],
                },
                {
                    "title": "Leap year rules",
                    "description": "Translate a real specification into conditions.",
                    "instructions": (
                        "Complete is_leap_year(year). A year is a leap year if it "
                        "is divisible by 4, except century years, unless divisible by 400."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def is_leap_year(year):\n    pass\n',
                    "solution": 'def is_leap_year(year):\n    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)\n',
                    "tests": 'assert is_leap_year(2024) is True\nassert is_leap_year(1900) is False\nassert is_leap_year(2000) is True\nassert is_leap_year(2023) is False\n',
                    "hints": [
                        "Use the modulo operator to test divisibility.",
                        "The century rule is an exception inside the divisible-by-4 rule.",
                    ],
                    "points": 12,
                    "minutes": 10,
                    "tags": ["python", "conditionals", "logic"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "truthiness-validation-nesting",
            "title": "Truthiness, Validation, and Avoiding the Nest",
            "description": (
                "Learn what Python considers true, build readable validation, and "
                "replace deep nesting with early exits and lookup tables."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "truthiness", "validation", "refactoring"],
            "objectives": [
                "Predict truthiness of common values",
                "Use explicit comparisons for optional values",
                "Refactor nested conditions into guard clauses",
            ],
            "resources": [
                {
                    "title": "Python docs — Truth Value Testing",
                    "url": "https://docs.python.org/3/library/stdtypes.html#truth-value-testing",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Truthiness, Validation, and Avoiding the Nest

## Truthiness is a shortcut with a cost

Python treats these as false:

```python
False
None
0
0.0
""
[]
{}
set()
```

Almost everything else is true. That makes this convenient:

```python
name = ""
if not name:
    print("Name required")
```

But it can hide intent. If `0` is a valid quantity, this is wrong:

```python
quantity = 0
if not quantity:
    print("Missing quantity")   # misleading
```

Be explicit when the difference between “absent” and “zero” matters:

```python
if quantity is None:
    print("Missing quantity")
elif quantity == 0:
    print("Quantity cannot be zero")
```

## Validation as a sequence of guards

```python
def validate_signup(email, password, age):
    problems = []
    if not email or "@" not in email:
        problems.append("A valid email is required")
    if len(password) < 8:
        problems.append("Password must be at least 8 characters")
    if not isinstance(age, int) or age < 13:
        problems.append("You must be at least 13")
    return problems
```

Returning every problem is often more useful than returning after the first. It lets the interface explain everything the user needs to fix.

## Replace nesting with decisions

Instead of:

```python
if user:
    if user["active"]:
        if user["role"] == "teacher":
            return "teacher dashboard"
```

Use guards:

```python
if not user:
    return "login"
if not user["active"]:
    return "inactive account"
if user["role"] == "teacher":
    return "teacher dashboard"
return "student dashboard"
```

Each line handles one case. The reader does not have to hold four nested conditions in working memory.

## Lookup tables instead of long chains

```python
COST = {"standard": 5, "express": 12, "pickup": 0}

def shipping(method):
    return COST.get(method, None)
```

When the mapping is data, represent it as data. Long `elif` chains that only compare strings are a signal.

## Common mistakes

- Treating `"0"` as false; it is a non-empty string and therefore true.
- Using `is` to compare numbers or strings.
- Hiding errors behind a bare `else`.
- Building a 200-line function of nested conditions instead of extracting small helpers.

## Guided practice

Predict:

```python
for value in [0, 1, "", "0", [], [0], None]:
    print(repr(value), bool(value))
```

Expected results: `0`, `""`, `[]`, and `None` are false; `1`, `"0"`, and `[0]` are true.

## Independent practice

Write `describe_access(role, active)` returning a clear sentence for admin, teacher, student, unknown role, and inactive accounts. Use guard clauses.

## Summary

Truthiness is useful but can blur “missing” and “empty”. Explicit checks, accumulated error lists, and guard clauses make decision-heavy code easier to trust.

## Further reading

- [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
''',
            "exercises": [
                {
                    "title": "Password validator",
                    "description": "Apply several rules and return useful feedback.",
                    "instructions": (
                        "Complete check_password(password). Return a list of problem "
                        "messages. Require at least 8 characters, one digit, and one "
                        "uppercase letter. Return [] when valid."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def check_password(password):\n    problems = []\n    # Add checks here\n    return problems\n',
                    "solution": 'def check_password(password):\n    problems = []\n    if len(password) < 8:\n        problems.append("too short")\n    if not any(ch.isdigit() for ch in password):\n        problems.append("needs a digit")\n    if not any(ch.isupper() for ch in password):\n        problems.append("needs an uppercase letter")\n    return problems\n',
                    "tests": 'assert check_password("abc") == ["too short", "needs a digit", "needs an uppercase letter"]\nassert check_password("Password1") == []\nassert check_password("password") == ["needs a digit", "needs an uppercase letter"]\n',
                    "hints": [
                        "Use any(...) with a generator to test characters.",
                        "Append messages in a predictable order so tests can compare lists.",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "validation", "strings"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 5 Assessment — Decisions",
        "description": "Check conditional ordering, truthiness, and validation design.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Why does an `if score >= 70` branch before `elif score >= 90` cause a problem for a score of 95?",
                "options": [
                    ("Only the first matching branch runs", True),
                    ("Python skips all later elif branches permanently", False),
                    ("The score is converted to a string", False),
                    ("The else branch always runs too", False),
                ],
                "explanation": "Conditional chains stop at the first true condition, so order encodes priority.",
            },
            {
                "content": "Which value is truthy?",
                "options": [("\"0\"", True), ("0", False), ("[]", False), ("None", False)],
                "explanation": "A non-empty string is truthy even when its content is the character 0.",
            },
            {
                "content": "What is a guard clause?",
                "options": [
                    ("An early return that handles an invalid or simplest case first", True),
                    ("A comment above a loop", False),
                    ("A password stored in code", False),
                    ("A special Python keyword", False),
                ],
                "explanation": "Guard clauses reduce nesting by handling the simple cases up front.",
            },
            {
                "content": "Which is the clearest check for a missing optional value where 0 is valid?",
                "options": [("value is None", True), ("not value", False), ("value == False", False), ("if value", False)],
                "explanation": "It distinguishes absence from a legitimate zero.",
            },
        ],
    },
    "projects": [],
}
