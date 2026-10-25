"""Module 10 — Files, JSON, CSV, and exceptions."""

MODULE = {
    "slug": "files-and-exceptions",
    "title": "Files, JSON, CSV, and Exceptions",
    "description": (
        "Make programs remember data. Read and write files safely, exchange "
        "structured data with JSON and CSV, and handle failures without hiding "
        "them."
    ),
    "objectives": [
        "Read and write text files with the with statement",
        "Parse and produce JSON",
        "Read CSV rows correctly, including quoted fields",
        "Catch specific exceptions and explain what failed",
    ],
    "estimated_duration_minutes": 115,
    "lessons": [
        {
            "slug": "reading-writing-files-and-paths",
            "title": "Reading and Writing Files Safely",
            "description": (
                "Paths, encodings, modes, and context managers — the details that "
                "prevent corrupted files and leaked handles."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "files", "paths", "context-manager"],
            "objectives": [
                "Use open() with an explicit encoding and mode",
                "Use with to close files reliably",
                "Read line by line without loading huge files into memory",
                "Write atomically enough for small scripts",
            ],
            "resources": [
                {
                    "title": "Python Tutorial — Reading and Writing Files",
                    "url": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files",
                    "resource_type": "reference",
                },
                {
                    "title": "pathlib documentation",
                    "url": "https://docs.python.org/3/library/pathlib.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Reading and Writing Files Safely

## The context manager

```python
with open("notes.txt", "w", encoding="utf-8") as handle:
    handle.write("First line\n")
    handle.write("Second line\n")
```

`with` closes the file even if an exception occurs. Always pass `encoding="utf-8"` for text; platform defaults vary and can corrupt non-ASCII text.

Modes:

- `"r"` read (default), fails if missing.
- `"w"` write, truncates an existing file.
- `"a"` append.
- `"x"` create, fails if it already exists.
- `"rb"`/`"wb"` binary.

## Reading

```python
with open("notes.txt", encoding="utf-8") as handle:
    content = handle.read()
```

For large files, iterate:

```python
with open("notes.txt", encoding="utf-8") as handle:
    for line_number, line in enumerate(handle, start=1):
        print(line_number, line.rstrip("\n"))
```

`readlines()` loads everything into memory; a loop does not.

## Paths without string archaeology

```python
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
path = data_dir / "notes.txt"

path.write_text("hello\n", encoding="utf-8")
print(path.read_text(encoding="utf-8"))
print(path.exists())
```

`pathlib` handles separators across operating systems. String concatenation with `"/"` is fragile.

## Avoid clobbering data

For a small script, write to a temporary file and replace the original only after success:

```python
from pathlib import Path

target = Path("tasks.json")
temp = target.with_suffix(".json.tmp")
temp.write_text('{"tasks": []}', encoding="utf-8")
temp.replace(target)
```

For serious applications, use a database or a library with transactional writes.

## Common mistakes

- Forgetting `encoding="utf-8"`.
- Opening with `"w"` when you meant `"a"`.
- Reading a file you never closed (without `with`).
- Assuming the current directory is the project directory.
- Catching `FileNotFoundError` and then continuing as if data existed.

## Guided practice

Create `log.txt` with three lines, then read and print only lines containing `ERROR`. Predict what `line.strip()` removes; note that it removes leading whitespace too, while `rstrip("\n")` is more precise.

## Independent practice

Write `tail(path, n)` returning the last `n` lines of a text file without reading the whole file into memory if the file is large. (A simple version may read all lines; then describe how you would improve it.)

## Summary

Use `with`, explicit encodings, and Path objects. Choose modes deliberately. Iterate when files may be large. Do not overwrite important data without a recovery path.

## Further reading

- [Reading and Writing Files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- [pathlib](https://docs.python.org/3/library/pathlib.html)
''',
            "exercises": [],
            "quiz": None,
        },
        {
            "slug": "json-csv-and-exception-handling",
            "title": "JSON, CSV, and Exception Handling",
            "description": (
                "Exchange structured data and design failure paths that inform "
                "the user instead of crashing the program."
            ),
            "difficulty": "intermediate",
            "minutes": 50,
            "tags": ["python", "json", "csv", "exceptions"],
            "objectives": [
                "Convert between Python objects and JSON",
                "Read CSV rows with the csv module",
                "Catch specific exceptions and preserve useful context",
                "Distinguish recoverable failures from bugs",
            ],
            "resources": [
                {
                    "title": "json module",
                    "url": "https://docs.python.org/3/library/json.html",
                    "resource_type": "reference",
                },
                {
                    "title": "csv module",
                    "url": "https://docs.python.org/3/library/csv.html",
                    "resource_type": "reference",
                },
                {
                    "title": "Python Tutorial — Errors and Exceptions",
                    "url": "https://docs.python.org/3/tutorial/errors.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# JSON, CSV, and Exception Handling

## JSON maps to ordinary Python values

```python
import json

data = {"name": "Ada", "topics": ["loops", "files"], "score": 92}
text = json.dumps(data, indent=2)
print(text)

restored = json.loads(text)
print(restored["topics"][0])
```

`dumps` → string; `loads` → Python object. For files, use `json.dump` and `json.load` with a handle.

JSON supports objects, arrays, strings, numbers, booleans, and null. Tuples become arrays; dictionary keys become strings. Custom objects are not serialisable by default.

```python
try:
    data = json.loads("{broken}")
except json.JSONDecodeError as exc:
    print(f"Invalid JSON at line {exc.lineno}, column {exc.colno}")
```

The exception object contains useful details. Do not throw them away.

## CSV is not just split(",")

```python
import csv
import io

raw = 'name,score\n"Ada, A.",92\nGrace,88\n'
reader = csv.DictReader(io.StringIO(raw))
for row in reader:
    print(row["name"], row["score"])
```

```text
Ada, A. 92
Grace 88
```

A quoted field can contain a comma. `split(",")` cannot handle that. Use the `csv` module.

Writing:

```python
output = io.StringIO()
writer = csv.DictWriter(output, fieldnames=["name", "score"])
writer.writeheader()
writer.writerow({"name": "Ada", "score": 92})
print(output.getvalue())
```

## Exceptions have a hierarchy

```python
try:
    value = int("abc")
except (TypeError, ValueError) as exc:
    print("Conversion failed:", exc)
```

Catch the most specific exception you can handle. A bare `except:` also catches `KeyboardInterrupt` and programming mistakes; avoid it.

Use `else` for code that should run only when no exception occurred, and `finally` for cleanup:

```python
try:
    handle = open("data.txt", encoding="utf-8")
except FileNotFoundError:
    print("No data file yet")
else:
    with handle:
        print(handle.read())
finally:
    print("Attempt finished")
```

## Raise with context

```python
def load_score(raw):
    if not raw.strip():
        raise ValueError("score cannot be empty")
    return int(raw)
```

Raising is appropriate when the caller cannot proceed. Returning `None` is appropriate when absence is a normal outcome. Choose deliberately and document it.

## Common mistakes

- Catching every exception and printing only “something went wrong”.
- Using `eval` to parse JSON.
- Treating CSV as simple comma-separated text.
- Writing files without `encoding="utf-8"`.
- Ignoring `JSONDecodeError` details that would make debugging easy.

## Guided practice

Predict:

```python
import json
print(json.loads('{"ok": true}')["ok"])
print(json.dumps(["a", 1, None]))
```

Expected `True` and `["a", 1, null]`.

## Independent practice

Write `load_tasks(path)` that returns a list, returns `[]` when the file is missing, and raises a clear `ValueError` when the JSON exists but is not a list.

## Summary

JSON handles nested records; CSV handles tabular rows. Use the standard modules rather than manual string splitting. Catch specific failures, preserve context, and distinguish normal absence from a real error.

## Further reading

- [json](https://docs.python.org/3/library/json.html)
- [csv](https://docs.python.org/3/library/csv.html)
- [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
''',
            "exercises": [
                {
                    "title": "Parse a JSON user record",
                    "description": "Defensive parsing with clear fallback values.",
                    "instructions": (
                        "Complete parse_user(raw). Parse JSON text and return a dict "
                        "with name, age, and active. Use 'Unknown', 0, and False as "
                        "defaults when fields are missing. Return None for invalid JSON."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'import json\n\n\ndef parse_user(raw):\n    pass\n',
                    "solution": 'import json\n\n\ndef parse_user(raw):\n    try:\n        data = json.loads(raw)\n    except (TypeError, json.JSONDecodeError):\n        return None\n    if not isinstance(data, dict):\n        return None\n    return {\n        "name": data.get("name", "Unknown"),\n        "age": data.get("age", 0),\n        "active": data.get("active", False),\n    }\n',
                    "tests": 'assert parse_user(\'{"name":"Ada","age":36,"active":true}\') == {"name":"Ada","age":36,"active":True}\nassert parse_user(\'{}\') == {"name":"Unknown","age":0,"active":False}\nassert parse_user("not json") is None\nassert parse_user(\'[1,2]\') is None\n',
                    "hints": [
                        "Use json.loads inside try/except.",
                        "Check isinstance(data, dict) before using .get.",
                    ],
                    "points": 12,
                    "minutes": 12,
                    "tags": ["python", "json", "exceptions"],
                },
                {
                    "title": "Parse CSV rows",
                    "description": "Use the csv module with quoted fields.",
                    "instructions": (
                        "Complete parse_scores(raw_csv). Return a list of "
                        "(name, int(score)) tuples using csv.DictReader. Skip rows "
                        "with an invalid score."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'import csv\nimport io\n\n\ndef parse_scores(raw_csv):\n    pass\n',
                    "solution": 'import csv\nimport io\n\n\ndef parse_scores(raw_csv):\n    rows = []\n    reader = csv.DictReader(io.StringIO(raw_csv))\n    for row in reader:\n        try:\n            score = int(row["score"])\n        except (KeyError, TypeError, ValueError):\n            continue\n        rows.append((row["name"], score))\n    return rows\n',
                    "tests": 'raw = "name,score\\n\\"Ada, A.\\",92\\nGrace,88\\nBad,nope\\n"\nassert parse_scores(raw) == [("Ada, A.", 92), ("Grace", 88)]\nassert parse_scores("name,score\\n") == []\n',
                    "hints": [
                        "Wrap the text in io.StringIO for csv.DictReader.",
                        "Continue past rows whose score cannot be converted.",
                    ],
                    "points": 12,
                    "minutes": 14,
                    "tags": ["python", "csv", "files"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 10 Assessment — Files and Data",
        "description": "Check safe file handling, structured data, and exceptions.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Why use `with open(...) as handle:`?",
                "options": [
                    ("It closes the file even when an exception occurs", True),
                    ("It makes reading faster", False),
                    ("It automatically parses JSON", False),
                    ("It prevents file-not-found errors", False),
                ],
                "explanation": "The context manager guarantees cleanup.",
            },
            {
                "content": "Which module should parse a CSV field containing a comma in quotes?",
                "options": [("csv", True), ("json", False), ("re alone", False), ("pathlib", False)],
                "explanation": "The csv module implements quoting and escaping rules.",
            },
            {
                "content": "What is the best exception handler for `int(input())`?",
                "options": [
                    ("except ValueError:", True),
                    ("except Exception: pass", False),
                    ("except:", False),
                    ("No handler; invalid input is a bug", False),
                ],
                "explanation": "Invalid numeric text raises ValueError; catch it specifically and respond.",
            },
            {
                "content": "Why is `except:` (bare) discouraged?",
                "options": [
                    ("It catches programming mistakes and interrupts, hiding real problems", True),
                    ("It is slower than Exception", False),
                    ("It only works in Python 2", False),
                    ("It cannot print errors", False),
                ],
                "explanation": "Catch the narrowest exception you can actually handle.",
            },
        ],
    },
    "projects": [
        {
            "title": "Expense Tracker",
            "description": (
                "Track spending by category, persist it to JSON, and produce a "
                "useful monthly summary."
            ),
            "requirements": (
                "1. Add expenses with date, amount, category, and note\n"
                "2. Validate amounts and dates\n"
                "3. Persist to JSON and reload safely\n"
                "4. Summarise by category and month\n"
                "5. Export a CSV report"
            ),
            "difficulty": "medium",
            "hours": 6,
            "tags": ["Python", "JSON", "CSV", "Functions"],
            "starter_files": {
                "expenses.py": "import json\nfrom pathlib import Path\n\nDATA = Path(\"expenses.json\")\n\n\ndef load_expenses():\n    if not DATA.exists():\n        return []\n    return json.loads(DATA.read_text(encoding=\"utf-8\"))\n\n\n# TODO: add, validate, summarise, and export\n"
            },
            "rubric": [
                {"criterion": "Totals and category summaries are accurate", "points": 30},
                {"criterion": "Corrupt or missing files do not destroy existing data", "points": 25},
                {"criterion": "Invalid amounts and dates are rejected", "points": 25},
                {"criterion": "Reports are readable and exportable", "points": 20},
            ],
        },
        {
            "title": "JSON Task Manager",
            "description": (
                "Build a small task manager with priorities, due dates, filters, "
                "and durable JSON storage."
            ),
            "requirements": (
                "1. Add, list, complete, and delete tasks\n"
                "2. Priority and due-date support with overdue warnings\n"
                "3. Filter by status and priority\n"
                "4. Persist to JSON with atomic replacement\n"
                "5. Handle a missing or corrupt data file without data loss"
            ),
            "difficulty": "medium",
            "hours": 5,
            "tags": ["Python", "JSON", "Files", "CLI"],
            "starter_files": {
                "tasks.py": "import json\nfrom pathlib import Path\n\nDATA = Path(\"tasks.json\")\n\n\ndef load_tasks():\n    if not DATA.exists():\n        return []\n    try:\n        return json.loads(DATA.read_text(encoding=\"utf-8\"))\n    except json.JSONDecodeError:\n        return []\n\n\n# TODO: implement add/list/complete/delete and persistence\n"
            },
            "rubric": [
                {"criterion": "All CRUD operations behave as specified", "points": 30},
                {"criterion": "Corrupt JSON is handled without crashing", "points": 25},
                {"criterion": "Storage and command handling are separated", "points": 25},
                {"criterion": "Output is clear and due dates are handled correctly", "points": 20},
            ],
        },
    ],
}
