"""Module 7 — Core collections."""

MODULE = {
    "slug": "collections",
    "title": "Lists, Tuples, Sets, and Dictionaries",
    "description": (
        "Choose the right container for the job: ordered sequences, immutable "
        "records, unique collections, and key-value mappings."
    ),
    "objectives": [
        "Create, index, slice, and modify lists",
        "Use tuples for fixed records and unpacking",
        "Deduplicate and compare data with sets",
        "Read, update, and iterate dictionaries safely",
    ],
    "estimated_duration_minutes": 110,
    "lessons": [
        {
            "slug": "lists-and-tuples",
            "title": "Lists and Tuples",
            "description": (
                "Store ordered data, mutate it deliberately, and recognise when "
                "an immutable tuple is the safer design."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "lists", "tuples", "slicing"],
            "objectives": [
                "Add, remove, and sort list items",
                "Explain the difference between a list and a tuple",
                "Unpack tuples into named variables",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Data Structures",
                    "url": "https://docs.python.org/3/tutorial/datastructures.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Lists and Tuples

## Lists are mutable sequences

```python
tasks = ["read", "practice", "review"]
tasks.append("sleep")
tasks[1] = "practice loops"
tasks.remove("sleep")
print(tasks)
```

```text
['read', 'practice loops', 'review']
```

Useful operations:

```python
tasks[0]          # read
tasks[-1]         # review
tasks[0:2]        # first two items
len(tasks)        # 3
"read" in tasks   # True
tasks.sort()      # in place, returns None
sorted(tasks)     # returns a new sorted list
```

The `.sort()` return value is a classic trap: it mutates the list and returns `None`.

## Slices create new lists

```python
numbers = [10, 20, 30, 40]
first_two = numbers[:2]
numbers[0] = 99
print(first_two)   # [10, 20] — unaffected
```

Slicing copies the selected references. For nested lists, the inner objects are still shared; that matters once collections contain collections.

## Tuples are immutable records

```python
point = (3, 5)
x, y = point
print(x, y)
```

Trying to change a tuple raises `TypeError`. That is the point: a tuple says “this combination is fixed.” Coordinates, RGB colours, and database rows are good fits.

A one-item tuple needs a comma:

```python
not_a_tuple = (5)
is_a_tuple = (5,)
```

## Mutability changes behaviour

```python
a = [1, 2]
b = a
b.append(3)
print(a)   # [1, 2, 3]
```

Both names point to the same list. If you want a copy:

```python
b = a.copy()
```

This distinction becomes critical when passing lists into functions.

## Common mistakes

- Assuming `sort()` returns a sorted list.
- Using a list as a dictionary key (unhashable).
- Forgetting the comma in a one-item tuple.
- Removing items while iterating over the same list.
- Confusing equality with identity for nested data.

## Guided practice

Predict:

```python
data = [3, 1, 2]
result = data.sort()
print(data)
print(result)
```

Expected output:

```text
[1, 2, 3]
None
```

### Hints

- sort changes the list in place.
- Functions with no return value return None.

## Independent practice

Write `unique_in_order(items)` that removes duplicates while preserving first-seen order. Do not use a set alone, because sets do not preserve order.

## Summary

Lists are ordered and mutable; tuples are ordered and immutable. Both support indexing, slicing, iteration, and unpacking. Mutability affects aliasing, copying, and function arguments.

## Further reading

- [Python Tutorial — Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
''',
            "exercises": [
                {
                    "title": "Deduplicate while preserving order",
                    "description": "Combine loops, membership checks, and lists.",
                    "instructions": (
                        "Complete unique_in_order(items). Keep the first occurrence "
                        "of each value and preserve the original order."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def unique_in_order(items):\n    pass\n',
                    "solution": 'def unique_in_order(items):\n    result = []\n    seen = set()\n    for item in items:\n        if item not in seen:\n            seen.add(item)\n            result.append(item)\n    return result\n',
                    "tests": 'assert unique_in_order([3, 1, 3, 2, 1]) == [3, 1, 2]\nassert unique_in_order([]) == []\nassert unique_in_order(["a", "b", "a"]) == ["a", "b"]\n',
                    "hints": [
                        "A set makes membership checks fast.",
                        "Append to the result only the first time you see a value.",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "lists", "sets"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "dictionaries-and-sets",
            "title": "Dictionaries and Sets",
            "description": (
                "Model records with keys, count frequencies, and use sets for "
                "uniqueness and fast membership tests."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "dictionaries", "sets", "counting"],
            "objectives": [
                "Read and update dictionary values safely",
                "Iterate over keys, values, and items",
                "Use sets for deduplication and membership",
                "Build a frequency counter",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Dictionaries",
                    "url": "https://docs.python.org/3/tutorial/datastructures.html#dictionaries",
                    "resource_type": "reference",
                },
                {
                    "title": "Python Tutorial — Sets",
                    "url": "https://docs.python.org/3/tutorial/datastructures.html#sets",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Dictionaries and Sets

## Dictionaries map keys to values

```python
student = {
    "name": "Ada",
    "score": 92,
    "topics": ["loops", "functions"],
}
print(student["name"])
print(student.get("email", "not provided"))
```

Use `[]` when a missing key is a bug. Use `.get()` when absence is expected.

```python
student["email"] = "ada@example.com"
student["score"] = 95
del student["topics"]
```

Keys must be hashable: strings, numbers, and tuples work; lists do not.

## Iteration

```python
for key in student:
    print(key)

for value in student.values():
    print(value)

for key, value in student.items():
    print(key, value)
```

Changing the dictionary's size while iterating raises a runtime error. Iterate over a copy (`list(student.items())`) or build a separate result.

## The frequency counter pattern

```python
def word_counts(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


print(word_counts("to be or not to be"))
```

```text
{'to': 2, 'be': 2, 'or': 1, 'not': 1}
```

This pattern appears in text analysis, log processing, inventories, and interviews. Learn it thoroughly.

## Sets are unique and unordered

```python
tags = {"python", "beginner", "python"}
print(tags)   # {'python', 'beginner'} in some order
```

Operations:

```python
a = {1, 2, 3}
b = {3, 4}
print(a | b)   # union
print(a & b)   # intersection
print(a - b)   # difference
```

Membership in a set is typically much faster than in a list for large collections.

## Nested data

```python
users = {
    "ada": {"score": 92, "active": True},
    "grace": {"score": 88, "active": False},
}

for name, profile in users.items():
    status = "active" if profile["active"] else "inactive"
    print(f"{name}: {profile['score']} ({status})")
```

Access nested keys one step at a time. If a level may be missing, use `.get()` with a deliberate default or validate the structure first.

## Common mistakes

- Using a list as a dictionary key.
- Assuming sets preserve insertion order (they do not guarantee it).
- Modifying a dictionary during iteration.
- Using `dict[key]` for optional keys and crashing on missing data.
- Building a frequency counter with a separate `if` for every word instead of `.get()`.

## Guided practice

Predict:

```python
counts = {}
for letter in "banana":
    counts[letter] = counts.get(letter, 0) + 1
print(counts["a"])
print(sorted(counts))
```

Expected `3` and `['a', 'b', 'n']`.

## Independent practice

Write `invert(mapping)` that swaps keys and values, returning a dictionary of lists when multiple keys share a value.

## Summary

Dictionaries model named fields and counts. Sets model uniqueness and set algebra. Learn `.get()`, `.items()`, and the frequency-counter pattern; they solve a huge range of practical problems.

## Further reading

- [Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
- [Sets](https://docs.python.org/3/tutorial/datastructures.html#sets)
''',
            "exercises": [
                {
                    "title": "Word frequency counter",
                    "description": "The canonical dictionary exercise.",
                    "instructions": (
                        "Complete word_counts(text). Lowercase the text, split on "
                        "whitespace, and return a dictionary of word counts. "
                        "Punctuation can be ignored for this exercise."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def word_counts(text):\n    pass\n',
                    "solution": 'def word_counts(text):\n    counts = {}\n    for word in text.lower().split():\n        counts[word] = counts.get(word, 0) + 1\n    return counts\n',
                    "tests": 'assert word_counts("to be or not to be") == {"to": 2, "be": 2, "or": 1, "not": 1}\nassert word_counts("") == {}\nassert word_counts("One one ONE") == {"one": 3}\n',
                    "hints": [
                        "Lowercase first so One and one count together.",
                        "Use counts.get(word, 0) + 1.",
                    ],
                    "points": 12,
                    "minutes": 10,
                    "tags": ["python", "dictionaries", "strings"],
                },
                {
                    "title": "Shared tags",
                    "description": "Use set intersection on real-looking data.",
                    "instructions": (
                        "Complete shared_tags(first, second) returning a sorted list "
                        "of tags that appear in both lists, without duplicates."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def shared_tags(first, second):\n    pass\n',
                    "solution": 'def shared_tags(first, second):\n    return sorted(set(first) & set(second))\n',
                    "tests": 'assert shared_tags(["python", "sql", "git"], ["git", "python", "api"]) == ["git", "python"]\nassert shared_tags([], ["x"]) == []\nassert shared_tags(["a", "a"], ["a"]) == ["a"]\n',
                    "hints": [
                        "Convert both lists to sets.",
                        "& is intersection; sorted returns a list.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "sets"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 7 Assessment — Collections",
        "description": "Test container choice, mutation, and counting patterns.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Which container is the best fit for a fixed RGB colour?",
                "options": [("A tuple", True), ("A list", False), ("A set", False), ("A dictionary", False)],
                "explanation": "A fixed ordered record with a known number of values is naturally a tuple.",
            },
            {
                "content": "What does `items.sort()` return?",
                "options": [("None", True), ("A new sorted list", False), ("The first item", False), ("True", False)],
                "explanation": "sort() mutates in place and returns None; use sorted() for a new list.",
            },
            {
                "content": "Why use a set for membership checks on a large collection?",
                "options": [
                    ("Set membership is typically constant-time on average", True),
                    ("Sets keep items in insertion order", False),
                    ("Sets allow duplicate values", False),
                    ("Sets can contain lists", False),
                ],
                "explanation": "Hash-based lookup is much faster than scanning a large list.",
            },
            {
                "content": "Which dictionary access is appropriate when a key may legitimately be absent?",
                "options": [("mapping.get(key, default)", True), ("mapping[key]", False), ("mapping.key", False), ("mapping.fetch(key)", False)],
                "explanation": "get() returns a default instead of raising KeyError.",
            },
        ],
    },
    "projects": [
        {
            "title": "Interactive Quiz Application",
            "description": (
                "Build a console quiz that loads questions, accepts answers, "
                "scores them, and reports a useful summary."
            ),
            "requirements": (
                "1. Store at least 10 questions with four options and one correct answer\n"
                "2. Shuffle question order without losing the answer key\n"
                "3. Validate input and allow one retry per question\n"
                "4. Track score, wrong answers, and time taken\n"
                "5. Print a revision list for missed topics"
            ),
            "difficulty": "medium",
            "hours": 4,
            "tags": ["Python", "Dictionaries", "Lists", "Control flow"],
            "starter_files": {
                "quiz.py": "QUESTIONS = [\n    {\n        \"prompt\": \"Which keyword defines a function?\",\n        \"options\": [\"def\", \"func\", \"fn\", \"lambda\"],\n        \"answer\": 0,\n        \"topic\": \"functions\",\n    },\n]\n\n# TODO: shuffle, ask, score, and summarise\n"
            },
            "rubric": [
                {"criterion": "Scoring and answer validation are accurate", "points": 30},
                {"criterion": "The quiz is playable without reading the source", "points": 25},
                {"criterion": "Question data is separated from presentation logic", "points": 25},
                {"criterion": "Invalid input never crashes the program", "points": 20},
            ],
        },
    ],
}
