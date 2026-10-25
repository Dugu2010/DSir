"""Module 6 — Loops and iteration."""

MODULE = {
    "slug": "loops-and-iteration",
    "title": "Loops, Iteration, and Problem Solving",
    "description": (
        "Repeat work without repeating code. Learn for and while loops, range, "
        "accumulators, break/continue, and the loop patterns that solve most "
        "beginner problems."
    ),
    "objectives": [
        "Write for loops over ranges and collections",
        "Choose between for and while",
        "Use accumulators, counters, and flags correctly",
        "Avoid infinite loops and off-by-one errors",
    ],
    "estimated_duration_minutes": 105,
    "lessons": [
        {
            "slug": "for-loops-and-range",
            "title": "for Loops and range()",
            "description": (
                "Iteration is how programs do useful work at scale. Learn the "
                "anatomy of a for loop and the patterns that recur everywhere."
            ),
            "difficulty": "beginner",
            "minutes": 40,
            "tags": ["python", "loops", "range", "iteration"],
            "objectives": [
                "Iterate over a range and over a list",
                "Explain range(start, stop, step)",
                "Build counters and accumulators",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — for Statements",
                    "url": "https://docs.python.org/3/tutorial/controlflow.html#for-statements",
                    "resource_type": "reference",
                },
                {
                    "title": "range() reference",
                    "url": "https://docs.python.org/3/library/stdtypes.html#range",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# for Loops and range()

## The shape

```python
for number in range(5):
    print(number)
```

```text
0
1
2
3
4
```

Read it as: “for each value produced by `range(5)`, bind it to `number` and run the indented block.”

`range(5)` is not a list. It is a lazy sequence of integers from `0` up to, but not including, `5`.

## range variations

```python
range(3)          # 0, 1, 2
range(2, 6)       # 2, 3, 4, 5
range(10, 0, -3)  # 10, 7, 4, 1
```

The stop value is excluded in every form. That is the source of most off-by-one bugs.

## Iterating over data

```python
names = ["Ada", "Grace", "Alan"]
for name in names:
    print(f"Hello, {name}")
```

When you need position and value:

```python
for index, name in enumerate(names, start=1):
    print(index, name)
```

`enumerate` is clearer than manually incrementing a counter.

## Accumulator pattern

```python
numbers = [4, 7, 2, 9, 1]
total = 0
for number in numbers:
    total += number
print(total)
```

`total += number` is shorthand for `total = total + number`. Start the accumulator at the identity value: `0` for sums, `1` for products, `[]` for a new list, `""` for text.

## Filtering while iterating

```python
evens = []
for number in numbers:
    if number % 2 == 0:
        evens.append(number)
print(evens)
```

```text
[4, 2]
```

Later, comprehensions will express this more compactly. Learn the loop first; the comprehension is a notation, not a different idea.

## Common mistakes

- Expecting `range(5)` to include `5`.
- Modifying a list while iterating over it.
- Forgetting to indent the body.
- Reinitialising the accumulator inside the loop.
- Using the loop variable after the loop when the collection was empty.

## Guided practice

Predict the output:

```python
total = 0
for value in range(1, 6):
    total += value
print(total)
```

Expected output: `15`.

### Hints

- Add the numbers 1 through 5.
- Trace the accumulator on paper if needed.

## Independent practice

Write a loop that prints the multiplication table for 7 from 1 to 10, formatted as `7 x 3 = 21`.

## Summary

`for` loops visit each item in a sequence. `range` generates integer sequences with an exclusive stop. Accumulators collect results across iterations.

## Further reading

- [Python Tutorial — for Statements](https://docs.python.org/3/tutorial/controlflow.html#for-statements)
''',
            "exercises": [
                {
                    "title": "Sum only even numbers",
                    "description": "Combine iteration, a conditional, and an accumulator.",
                    "instructions": (
                        "Complete sum_evens(numbers) returning the sum of even "
                        "integers. Return 0 for an empty list. Do not use sum() "
                        "with a generator; practise the loop."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def sum_evens(numbers):\n    pass\n',
                    "solution": 'def sum_evens(numbers):\n    total = 0\n    for number in numbers:\n        if number % 2 == 0:\n            total += number\n    return total\n',
                    "tests": 'assert sum_evens([1, 2, 3, 4, 5, 6]) == 12\nassert sum_evens([]) == 0\nassert sum_evens([1, 3, 5]) == 0\n',
                    "hints": [
                        "Start total at 0.",
                        "Use number % 2 == 0 to test evenness.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "loops", "conditionals"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "while-break-continue-patterns",
            "title": "while Loops, break/continue, and Real Patterns",
            "description": (
                "Use while when the number of repetitions is unknown, control "
                "loop exits carefully, and solve counting, searching, and "
                "validation problems."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "while", "break", "continue", "problem-solving"],
            "objectives": [
                "Write a while loop with a clear termination condition",
                "Use break and continue without creating confusing flow",
                "Implement count, search, and retry patterns",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — while Statements",
                    "url": "https://docs.python.org/3/tutorial/introduction.html#first-steps-towards-programming",
                    "resource_type": "reference",
                },
                {
                    "title": "MIT OCW 6.100L — Iteration and loops",
                    "url": "https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# while Loops, break/continue, and Real Patterns

## Use while when you do not know the count

```python
attempts = 0
while attempts < 3:
    print("Try again")
    attempts += 1
```

The loop continues while the condition is true. Something inside must move the condition toward false, or you have an infinite loop.

## A retry loop

```python
raw = ""
while not raw.isdigit():
    raw = input("Enter a whole number: ")
print(int(raw))
```

This repeats until the user enters digits. In a real program, also provide a way to quit. An unconditional loop that depends on a user is a usability risk.

## break exits immediately

```python
numbers = [3, 8, 11, 14, 17]
for number in numbers:
    if number % 2 == 0:
        print("First even:", number)
        break
```

```text
First even: 8
```

`break` leaves the nearest enclosing loop. If you need the value after the loop, initialise it before:

```python
first_even = None
for number in numbers:
    if number % 2 == 0:
        first_even = number
        break
```

## continue skips the rest of this iteration

```python
for number in range(1, 8):
    if number % 2 == 0:
        continue
    print(number)
```

```text
1
3
5
7
```

Use `continue` when the skipped case is easy to state and the remaining work is the main path. Too many `continue`s can make flow hard to follow.

## The while-else trap

Python supports `else` on loops, executed when the loop finishes without `break`. It surprises most beginners. Do not use it until you can explain it clearly; an explicit flag is more readable.

## Counting, searching, validating

```python
def count_words(text):
    count = 0
    for word in text.split():
        count += 1
    return count


def contains(items, target):
    for item in items:
        if item == target:
            return True
    return False


def all_positive(numbers):
    for number in numbers:
        if number <= 0:
            return False
    return True
```

These three patterns — count, search, validate-all — cover a huge share of everyday loops.

## Common mistakes

- Forgetting to update the variable that controls a while loop.
- Changing a list while looping over it.
- Using `break` inside nested loops and expecting both loops to stop.
- Putting the return statement inside the loop when the answer needs every item checked.

## Guided practice

How many times does this print?

```python
count = 0
while count < 5:
    print(count)
    count += 2
```

It prints `0`, `2`, `4` — three times. The condition is checked before each iteration.

## Independent practice

Write `first_negative(numbers)` returning the first negative number or `None`. Then write `all_even(numbers)` returning a boolean.

## Summary

While loops handle unknown repetition; for loops handle collections. `break` exits, `continue` skips. Most loop problems are counting, searching, validating, or accumulating.

## Further reading

- [Python Tutorial — while loops](https://docs.python.org/3/tutorial/introduction.html#first-steps-towards-programming)
- [Python reference — break and continue](https://docs.python.org/3/reference/simple_stmts.html#break)
''',
            "exercises": [
                {
                    "title": "FizzBuzz list",
                    "description": "A classic loop-and-conditional problem with strict output.",
                    "instructions": (
                        "Complete fizzbuzz(limit) returning a list from 1 to limit "
                        "where multiples of 3 are 'Fizz', multiples of 5 are 'Buzz', "
                        "multiples of both are 'FizzBuzz', and others are numbers."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def fizzbuzz(limit):\n    result = []\n    # Build the list\n    return result\n',
                    "solution": 'def fizzbuzz(limit):\n    result = []\n    for number in range(1, limit + 1):\n        if number % 15 == 0:\n            result.append("FizzBuzz")\n        elif number % 3 == 0:\n            result.append("Fizz")\n        elif number % 5 == 0:\n            result.append("Buzz")\n        else:\n            result.append(number)\n    return result\n',
                    "tests": 'assert fizzbuzz(5) == [1, 2, "Fizz", 4, "Buzz"]\nassert fizzbuzz(15)[-1] == "FizzBuzz"\nassert fizzbuzz(0) == []\n',
                    "hints": [
                        "Check divisibility by 15 before 3 or 5.",
                        "range(1, limit + 1) includes limit.",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "loops", "conditionals"],
                },
                {
                    "title": "First failure finder",
                    "description": "Practice early exit and return values.",
                    "instructions": (
                        "Complete first_invalid(scores) returning the first score "
                        "outside 0–100, or None if all are valid."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def first_invalid(scores):\n    pass\n',
                    "solution": 'def first_invalid(scores):\n    for score in scores:\n        if score < 0 or score > 100:\n            return score\n    return None\n',
                    "tests": 'assert first_invalid([80, 90, -1, 101]) == -1\nassert first_invalid([0, 100]) is None\nassert first_invalid([]) is None\n',
                    "hints": [
                        "Return as soon as an invalid score is found.",
                        "After the loop finishes, return None.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "loops", "search"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 6 Assessment — Loops",
        "description": "Check range bounds, accumulation, and loop control.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What does `list(range(2, 8, 2))` produce?",
                "options": [("[2, 4, 6]", True), ("[2, 4, 6, 8]", False), ("[2, 3, 4, 5, 6, 7]", False), ("[4, 6, 8]", False)],
                "explanation": "Start at 2, stop before 8, step by 2.",
            },
            {
                "content": "Where should an accumulator for a sum be initialised?",
                "options": [
                    ("Before the loop, at 0", True),
                    ("Inside the loop, at 0", False),
                    ("After the loop", False),
                    ("Inside the loop, at 1", False),
                ],
                "explanation": "Reinitialising inside the loop discards previous iterations.",
            },
            {
                "content": "What does break do?",
                "options": [
                    ("Exits the nearest enclosing loop immediately", True),
                    ("Skips the current iteration only", False),
                    ("Restarts the loop from zero", False),
                    ("Raises an exception", False),
                ],
                "explanation": "continue skips one iteration; break leaves the loop entirely.",
            },
            {
                "content": "A while loop never ends. What is the most likely cause?",
                "options": [
                    ("The condition never becomes false", True),
                    ("The loop body is indented", False),
                    ("The loop uses print", False),
                    ("Python has a loop limit", False),
                ],
                "explanation": "Every while loop needs progress toward termination or a deliberate break.",
            },
        ],
    },
    "projects": [
        {
            "title": "Number Guessing Game",
            "description": (
                "Build a command-line game where the computer chooses a number "
                "and the player guesses with higher/lower feedback."
            ),
            "requirements": (
                "1. Generate a random number between 1 and 100\n"
                "2. Let the player guess repeatedly with clear higher/lower feedback\n"
                "3. Limit attempts and show the number when the player loses\n"
                "4. Validate non-numeric input without crashing\n"
                "5. Offer a replay option and track wins"
            ),
            "difficulty": "easy",
            "hours": 3,
            "tags": ["Python", "Loops", "Random", "Input validation"],
            "starter_files": {
                "guessing_game.py": "import random\n\n\ndef play():\n    secret = random.randint(1, 100)\n    attempts = 0\n    # TODO: loop until the player guesses or runs out of attempts\n\n\nif __name__ == \"__main__\":\n    play()\n"
            },
            "rubric": [
                {"criterion": "Game ends correctly for win and loss", "points": 30},
                {"criterion": "Invalid input is handled gracefully", "points": 25},
                {"criterion": "Functions are small and named clearly", "points": 20},
                {"criterion": "Tests high, low, invalid, and exact guesses", "points": 25},
            ],
        },
    ],
}
