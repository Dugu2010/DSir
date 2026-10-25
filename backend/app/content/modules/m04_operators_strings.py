"""Module 4 — Operators and strings."""

MODULE = {
    "slug": "operators-and-strings",
    "title": "Operators and Strings",
    "description": (
        "Use arithmetic, comparison, and logical operators correctly, then learn "
        "to slice, search, clean, and format text — the data type you will handle "
        "in almost every program."
    ),
    "objectives": [
        "Apply arithmetic operators and explain floor division and modulo",
        "Combine comparisons with and/or/not",
        "Index, slice, and iterate over strings",
        "Use common string methods without mutating the original",
    ],
    "estimated_duration_minutes": 100,
    "lessons": [
        {
            "slug": "arithmetic-comparison-logical-operators",
            "title": "Arithmetic, Comparison, and Logical Operators",
            "description": (
                "Operators are small tools with sharp edges. Learn precedence, "
                "integer versus float division, and how comparisons compose."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "operators", "expressions", "logic"],
            "objectives": [
                "Predict the result of mixed arithmetic expressions",
                "Explain /, //, %, and **",
                "Combine comparison results with boolean operators",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — More Control Flow Tools (expressions preview)",
                    "url": "https://docs.python.org/3/tutorial/controlflow.html",
                    "resource_type": "reference",
                },
                {
                    "title": "Expressions reference",
                    "url": "https://docs.python.org/3/reference/expressions.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Arithmetic, Comparison, and Logical Operators

## Arithmetic with two personalities

```python
print(10 / 3)    # 3.3333333333333335  (true division, always float)
print(10 // 3)   # 3                   (floor division)
print(10 % 3)    # 1                   (remainder)
print(10 ** 3)   # 1000                (power)
```

The distinction between `/` and `//` matters beyond arithmetic. `//` floors toward negative infinity:

```python
print(-7 // 2)   # -4
print(-7 % 2)    # 1
```

This is not a bug. Floor division answers “how many whole groups fit, rounding down?” and modulo is defined consistently with it.

## Precedence

Python evaluates `**`, then unary operators, then `* / // %`, then `+ -`, then comparisons, then `not`, then `and`, then `or`.

```python
print(2 + 3 * 4)      # 14, not 20
print((2 + 3) * 4)    # 20
```

Use parentheses when a reader would have to think. Clever precedence is not a personality trait worth cultivating.

## Comparisons return booleans

```python
print(5 > 3)          # True
print(5 == 5.0)       # True
print("5" == 5)       # False
print(0 <= score <= 100)  # chained comparison
```

`==` compares values; `is` compares object identity. For beginner code, use `is` mainly with `None`.

## Boolean operators

```python
age = 20
has_ticket = True
print(age >= 18 and has_ticket)   # True
print(age < 13 or has_ticket)     # True
print(not has_ticket)             # False
```

`and` and `or` short-circuit: they stop as soon as the result is known. That makes this safe:

```python
name = None
if name is not None and name.strip():
    print("valid")
```

If `name` is `None`, the second check never runs.

## Common mistakes

- Using `=` where `==` is needed.
- Assuming `/` returns an integer.
- Writing `not x == y` when `x != y` is clearer.
- Comparing a string to a number and expecting conversion.
- Using `or` to provide a default when `0` or `""` are legitimate values; use an explicit `is None` check.

## Guided practice

Predict each line, then run:

```python
print(7 // 2)
print(7 % 2)
print(2 ** 3 ** 2)
print(3 > 2 and 1 > 2)
```

Expected output:

```text
3
1
512
False
```

`2 ** 3 ** 2` is right-associative: `2 ** 9`.

### Hints

- Parentheses are your friend.
- `and` requires both sides to be truthy.

## Independent practice

Write expressions that answer: is a number even? is it between 10 and 20 inclusive? is a username non-empty and not equal to `"admin"`?

## Summary

Operators compose into expressions. Know the division variants, use parentheses for clarity, and combine only comparisons that genuinely belong together.

## Further reading

- [Python reference — Expressions](https://docs.python.org/3/reference/expressions.html)
- [Python Tutorial — An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html)
''',
            "exercises": [
                {
                    "title": "Split a bill correctly",
                    "description": "Practice floor division and remainders.",
                    "instructions": (
                        "Complete split_bill(total_cents, people). Return a tuple "
                        "(each_pays, remainder) where each_pays is floor division "
                        "and remainder is what is left over."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def split_bill(total_cents, people):\n    pass\n',
                    "solution": 'def split_bill(total_cents, people):\n    return total_cents // people, total_cents % people\n',
                    "tests": 'assert split_bill(1000, 3) == (333, 1)\nassert split_bill(1200, 4) == (300, 0)\nassert split_bill(5, 2) == (2, 1)\n',
                    "hints": [
                        "Use // for the equal share and % for the leftover cents.",
                        "A tuple can be written as a, b.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "operators", "tuples"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "strings-indexing-slicing-methods",
            "title": "Strings: Indexing, Slicing, and Useful Methods",
            "description": (
                "Treat text as a sequence: access characters, take slices, clean "
                "input, split, join, and format output."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "strings", "slicing", "methods"],
            "objectives": [
                "Index and slice strings safely",
                "Use split, join, strip, replace, and case methods",
                "Explain why string methods return new strings",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Strings",
                    "url": "https://docs.python.org/3/tutorial/introduction.html#strings",
                    "resource_type": "reference",
                },
                {
                    "title": "String methods reference",
                    "url": "https://docs.python.org/3/library/stdtypes.html#string-methods",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Strings: Indexing, Slicing, and Useful Methods

## Strings are sequences

```python
word = "python"
print(word[0])     # p
print(word[-1])    # n
print(word[0:3])   # pyt  (start included, stop excluded)
print(word[::2])   # pto
```

Indexing starts at `0`. A slice `[start:stop]` includes `start` and excludes `stop`. Negative indices count from the end.

Out-of-range indexing raises `IndexError`:

```python
print(word[100])
```

Slicing past the end does not:

```python
print(word[0:100])  # python
```

## Strings are immutable

```python
name = "ada"
name.upper()
print(name)   # ada — the method returned a new string
```

You must assign the result:

```python
name = name.upper()
print(name)   # ADA
```

This is a frequent source of silent bugs. `strip()`, `replace()`, and `lower()` also return new strings.

## Cleaning input

```python
raw = "  Ada Lovelace  "
clean = raw.strip()
print(f"[{clean}]")
```

```text
[Ada Lovelace]
```

Useful methods:

```python
"hello".startswith("he")    # True
"hello".endswith("lo")      # True
"a,b,c".split(",")          # ['a', 'b', 'c']
"-".join(["2026", "10"])    # '2026-10'
"banana".replace("a", "o")  # 'bonono'
"42".isdigit()              # True
```

## f-strings do more than insert values

```python
price = 9.5
print(f"Total: {price:.2f}")
print(f"Name: {'Ada':>10}")
```

```text
Total: 9.50
Name:        Ada
```

Format specs let you align columns and control decimals without manual padding.

## Common mistakes

- Forgetting that slices exclude the stop index.
- Assuming `.strip()` changes the original variable.
- Using `int(" 42 ")` — strip text first if user input may contain spaces.
- Joining with a list of non-strings.

## Guided practice

Predict the output:

```python
text = "DSir Academy"
print(text[0:4])
print(text[-7:])
print(text.lower().split())
```

Expected output:

```text
DSir
Academy
['dsir', 'academy']
```

### Hints

- `[0:4]` includes indices 0, 1, 2, 3.
- `split()` with no argument splits on whitespace.

## Independent practice

Write `clean_name(text)`: strip spaces, collapse multiple spaces, and title-case the result. Test `"  ada   lovelace "` → `"Ada Lovelace"`.

## Summary

Strings are indexed sequences of characters. Methods return new values. Slicing is safe at the edges; indexing is not. Clean input early and format output deliberately.

## Further reading

- [String methods](https://docs.python.org/3/library/stdtypes.html#string-methods)
- [Format String Syntax](https://docs.python.org/3/library/string.html#formatstrings)
''',
            "exercises": [
                {
                    "title": "Palindrome checker",
                    "description": "Combine slicing, normalisation, and comparison.",
                    "instructions": (
                        "Complete is_palindrome(text). Ignore case and spaces. "
                        "Return True when the cleaned text reads the same backwards."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def is_palindrome(text):\n    pass\n',
                    "solution": 'def is_palindrome(text):\n    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())\n    return cleaned == cleaned[::-1]\n',
                    "tests": 'assert is_palindrome("Racecar") is True\nassert is_palindrome("A man a plan a canal Panama") is True\nassert is_palindrome("Python") is False\nassert is_palindrome("") is True\n',
                    "hints": [
                        "Keep only alphanumeric characters and lowercase them.",
                        "Reversing a string uses [::-1].",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "strings", "slicing"],
                },
                {
                    "title": "Initials from a name",
                    "description": "Practice split, indexing, and join.",
                    "instructions": (
                        "Complete initials(full_name) so 'Ada Lovelace' becomes "
                        "'A.L.'. Ignore extra spaces and return an empty string for blank input."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def initials(full_name):\n    pass\n',
                    "solution": 'def initials(full_name):\n    parts = full_name.split()\n    return ".".join(part[0].upper() for part in parts) + ("." if parts else "")\n',
                    "tests": 'assert initials("Ada Lovelace") == "A.L."\nassert initials("  grace   hopper ") == "G.H."\nassert initials("") == ""\n',
                    "hints": [
                        "split() with no arguments ignores repeated spaces.",
                        "Build each initial, then join with dots and add one final dot.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "strings", "split"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 4 Assessment — Operators and Strings",
        "description": "Test operator behaviour, slicing, and string methods.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What is `-7 // 2` in Python?",
                "options": [("-4", True), ("-3", False), ("-3.5", False), ("3", False)],
                "explanation": "Floor division rounds toward negative infinity, so -3.5 floors to -4.",
            },
            {
                "content": "What does `\"python\"[1:4]` return?",
                "options": [("yth", True), ("ytho", False), ("pyt", False), ("tho", False)],
                "explanation": "Slices include the start and exclude the stop: indices 1, 2, 3.",
            },
            {
                "content": "After `name = \"ada\"; name.upper()`, what is name?",
                "options": [
                    ("'ada' because strings are immutable", True),
                    ("'ADA' because upper changes it in place", False),
                    ("None", False),
                    ("An error", False),
                ],
                "explanation": "upper() returns a new string; the original binding is unchanged unless reassigned.",
            },
            {
                "content": "Which expression is safest for checking that a possibly-missing name is non-empty?",
                "options": [
                    ("name is not None and name.strip()", True),
                    ("name.strip() is not None", False),
                    ("not name == None", False),
                    ("name or None", False),
                ],
                "explanation": "The explicit None check short-circuits before calling strip on None.",
            },
        ],
    },
    "projects": [],
}
