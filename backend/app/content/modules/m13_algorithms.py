"""Module 13 — Algorithms and complexity."""

MODULE = {
    "slug": "algorithms-and-complexity",
    "title": "Algorithms, Searching, and Complexity",
    "description": (
        "Develop algorithmic problem-solving habits: clarify the input, choose a "
        "strategy, test edge cases, and reason about time and space without "
        "getting lost in notation."
    ),
    "objectives": [
        "Compare linear and binary search",
        "Implement a simple sort and explain its trade-offs",
        "Interpret common Big-O growth rates",
        "Choose data structures based on access patterns",
    ],
    "estimated_duration_minutes": 105,
    "lessons": [
        {
            "slug": "searching-sorting-and-tradeoffs",
            "title": "Searching, Sorting, and Trade-offs",
            "description": (
                "Two fundamental operations, one recurring lesson: the right data "
                "structure changes what is cheap."
            ),
            "difficulty": "intermediate",
            "minutes": 50,
            "tags": ["python", "algorithms", "searching", "sorting"],
            "objectives": [
                "Implement linear and binary search",
                "Explain why binary search requires sorted data",
                "Trace an insertion sort",
            ],
            "resources": [
                {
                    "title": "MIT OCW 6.100L — Algorithmic complexity",
                    "url": "https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — Sorting HOW TO",
                    "url": "https://docs.python.org/3/howto/sorting.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Searching, Sorting, and Trade-offs

## Clarify before coding

“Find an item” is underspecified. Ask:

- Is the collection sorted?
- Can values repeat?
- Do we need the index or just existence?
- How often will we search versus modify?

The answers decide the algorithm.

## Linear search

```python
def linear_search(items, target):
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1
```

Time: proportional to the number of items — **O(n)**. It works on unsorted data and is perfectly appropriate for small lists.

## Binary search

```python
def binary_search(sorted_items, target):
    low, high = 0, len(sorted_items) - 1
    while low <= high:
        middle = (low + high) // 2
        value = sorted_items[middle]
        if value == target:
            return middle
        if value < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1
```

Binary search halves the remaining range each step — **O(log n)**. It requires sorted data. Sorting first costs O(n log n), so binary search pays off when you search many times.

### Off-by-one check

The `while low <= high` condition and `middle ± 1` updates are where most binary-search bugs live. Test with empty lists, one item, first item, last item, and missing values.

## Insertion sort

```python
def insertion_sort(items):
    result = list(items)
    for index in range(1, len(result)):
        current = result[index]
        position = index - 1
        while position >= 0 and result[position] > current:
            result[position + 1] = result[position]
            position -= 1
        result[position + 1] = current
    return result
```

It builds a sorted prefix. Average and worst case are **O(n²)**, but it is fast for nearly sorted data and easy to reason about. Python's built-in `sorted` uses Timsort and should be your default in real code.

## Use the built-ins

```python
sorted(values)
sorted(records, key=lambda record: record["score"], reverse=True)
values.sort()
```

Writing a sort is an educational exercise; reaching for a manual sort in production without a measured reason is usually a mistake.

## Common mistakes

- Running binary search on unsorted data.
- Returning the value when the caller needs the index.
- Forgetting duplicate values when specifying behaviour.
- Sorting inside a loop repeatedly instead of once.
- Optimising before measuring.

## Guided practice

Trace `binary_search([1, 3, 5, 7, 9], 7)` and record low, high, and middle each iteration. How many iterations? Two.

## Independent practice

Implement `count_occurrences(sorted_items, target)` using binary search to find the bounds. Compare its complexity with a linear count.

## Summary

Linear search is simple and works anywhere. Binary search is fast but needs order. Simple sorts teach invariants; built-in sorting is the practical default. Choose based on data shape and access patterns.

## Further reading

- [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [MIT OCW 6.100L](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/)
''',
            "exercises": [
                {
                    "title": "Binary search",
                    "description": "Implement the classic divide-and-conquer search.",
                    "instructions": (
                        "Complete binary_search(items, target) for a sorted list. "
                        "Return the index or -1. Handle empty and one-item lists."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def binary_search(items, target):\n    pass\n',
                    "solution": 'def binary_search(items, target):\n    low, high = 0, len(items) - 1\n    while low <= high:\n        middle = (low + high) // 2\n        if items[middle] == target:\n            return middle\n        if items[middle] < target:\n            low = middle + 1\n        else:\n            high = middle - 1\n    return -1\n',
                    "tests": 'assert binary_search([1, 2, 3, 4, 5], 1) == 0\nassert binary_search([1, 2, 3, 4, 5], 5) == 4\nassert binary_search([1, 2, 3, 4, 5], 9) == -1\nassert binary_search([], 1) == -1\nassert binary_search([7], 7) == 0\n',
                    "hints": [
                        "Use a low and high index and shrink the range.",
                        "Update low to middle + 1 and high to middle - 1.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "algorithms", "searching"],
                },
                {
                    "title": "Insertion sort",
                    "description": "Trace and implement a stable comparison sort.",
                    "instructions": (
                        "Complete insertion_sort(items) returning a new sorted list "
                        "without modifying the input."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def insertion_sort(items):\n    pass\n',
                    "solution": 'def insertion_sort(items):\n    result = list(items)\n    for index in range(1, len(result)):\n        current = result[index]\n        position = index - 1\n        while position >= 0 and result[position] > current:\n            result[position + 1] = result[position]\n            position -= 1\n        result[position + 1] = current\n    return result\n',
                    "tests": 'original = [4, 2, 7, 1]\nassert insertion_sort(original) == [1, 2, 4, 7]\nassert original == [4, 2, 7, 1]\nassert insertion_sort([]) == []\nassert insertion_sort([3, 3, 1]) == [1, 3, 3]\n',
                    "hints": [
                        "Copy the input first with list(items).",
                        "Shift larger values right, then insert current in the gap.",
                    ],
                    "points": 15,
                    "minutes": 16,
                    "tags": ["python", "algorithms", "sorting"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "big-o-without-panic",
            "title": "Big-O Without the Maths Panic",
            "description": (
                "A practical reading of complexity: what grows, what stays "
                "constant, and why the hidden constant still matters."
            ),
            "difficulty": "intermediate",
            "minutes": 35,
            "tags": ["python", "algorithms", "complexity"],
            "objectives": [
                "Recognise O(1), O(log n), O(n), O(n log n), and O(n²)",
                "Estimate the cost of common Python operations",
                "Explain why Big-O ignores constants but engineering does not",
            ],
            "resources": [
                {
                    "title": "Python wiki — TimeComplexity",
                    "url": "https://wiki.python.org/moin/TimeComplexity",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Big-O Without the Maths Panic

## Big-O describes growth

If input size is `n`, we ask: how does the work grow as `n` grows?

- **O(1)** — same time regardless of size. Dictionary lookup, list index.
- **O(log n)** — halves the problem. Binary search.
- **O(n)** — visit each item once. Linear search, one loop.
- **O(n log n)** — efficient comparison sorting.
- **O(n²)** — nested loops over the same input.

Big-O ignores constants and lower-order terms. `3n + 20` is O(n). That does not mean constants are irrelevant; it means they do not change the growth category.

## Reading loops

```python
def total(items):          # O(n): one pass
    result = 0
    for item in items:
        result += item
    return result


def pairs(items):          # O(n²): nested pass over the same data
    result = []
    for first in items:
        for second in items:
            result.append((first, second))
    return result


def contains_duplicates(items):
    seen = set()           # average O(n) time, O(n) space
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
```

The set trades memory for speed. That is a real engineering choice, not a violation of algorithmic purity.

## Common Python costs

- List append: amortised O(1).
- List insert at the front: O(n).
- Dictionary/set membership: average O(1).
- `in` on a list: O(n).
- Sorting: O(n log n).
- String concatenation in a loop: often O(n²); use `"".join(parts)`.

## When Big-O is not the whole story

For 20 items, an O(n²) loop may be faster than an O(n log n) algorithm because of constants and cache behaviour. Measure with representative data before optimising.

```python
import time

start = time.perf_counter()
# work
elapsed = time.perf_counter() - start
print(f"{elapsed:.4f}s")
```

Benchmarking without a baseline is just guessing with extra steps.

## Common mistakes

- Calling every nested loop O(n²) when the inner loop runs a fixed number of times.
- Ignoring memory usage.
- Optimising code that is not the bottleneck.
- Confusing worst case with average case.

## Guided practice

Classify `for item in items: for tag in item.tags:` — it is O(n × m), not necessarily O(n²), where `m` is the average number of tags.

## Summary

Big-O is a vocabulary for growth. Use it to reject clearly bad designs, then measure real performance. Data structures are often a better lever than micro-optimising a loop.

## Further reading

- [Python TimeComplexity](https://wiki.python.org/moin/TimeComplexity)
''',
            "exercises": [],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 13 Assessment — Algorithms",
        "description": "Check search preconditions, complexity, and trade-offs.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What precondition does binary search require?",
                "options": [("The collection is sorted", True), ("The collection has no duplicates", False), ("The collection is a set", False), ("The target is an integer", False)],
                "explanation": "Binary search discards half the range based on ordering.",
            },
            {
                "content": "What is the time complexity of one loop over n items?",
                "options": [("O(n)", True), ("O(1)", False), ("O(n²)", False), ("O(log n)", False)],
                "explanation": "The work grows linearly with the input size.",
            },
            {
                "content": "Why is `\"\".join(parts)` usually preferred to repeated `text += part` in a loop?",
                "options": [
                    ("It avoids repeatedly copying the growing string", True),
                    ("It sorts the parts", False),
                    ("It removes duplicates", False),
                    ("It works only with numbers", False),
                ],
                "explanation": "Repeated concatenation can become quadratic; join builds the result efficiently.",
            },
            {
                "content": "When should you measure performance?",
                "options": [
                    ("On representative data before and after a change", True),
                    ("Only on an empty list", False),
                    ("After every line you type", False),
                    ("Never; Big-O is enough", False),
                ],
                "explanation": "Measurements reveal real bottlenecks and validate claimed improvements.",
            },
        ],
    },
    "projects": [],
}
