"""Module 16 — SQL, databases, and Python integration."""

MODULE = {
    "slug": "sql-and-databases",
    "title": "SQL, Databases, and Python",
    "description": (
        "Store data properly: design tables, write safe parameterised queries, "
        "model relationships, and use transactions so partial failures do not "
        "corrupt your data."
    ),
    "objectives": [
        "Create tables with keys and constraints",
        "Write SELECT, INSERT, UPDATE, and DELETE safely",
        "Join related tables",
        "Use sqlite3 with parameters and transactions",
        "Recognise SQL injection risks",
    ],
    "estimated_duration_minutes": 130,
    "lessons": [
        {
            "slug": "relational-basics-and-sql",
            "title": "Relational Basics and SQL",
            "description": (
                "Tables, rows, keys, and the four queries that cover most "
                "day-to-day data work."
            ),
            "difficulty": "beginner",
            "minutes": 55,
            "tags": ["python", "sql", "database", "sqlite"],
            "objectives": [
                "Explain primary and foreign keys",
                "Write filtered, ordered SELECT queries",
                "Use joins to combine tables",
            ],
            "resources": [
                {
                    "title": "Python docs — sqlite3",
                    "url": "https://docs.python.org/3/library/sqlite3.html",
                    "resource_type": "reference",
                },
                {
                    "title": "SQLite documentation",
                    "url": "https://www.sqlite.org/docs.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Relational Basics and SQL

## Tables are typed rows

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    score REAL CHECK (score BETWEEN 0 AND 100)
);
```

- **Primary key** uniquely identifies a row.
- **NOT NULL** prevents missing values.
- **CHECK** rejects invalid data at the database boundary.
- **Foreign key** points at a row in another table, modelling a relationship.

```sql
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    exercise TEXT NOT NULL,
    passed INTEGER NOT NULL DEFAULT 0
);
```

## Reading data

```sql
SELECT name, score
FROM students
WHERE cohort = '2026-spring' AND score >= 70
ORDER BY score DESC
LIMIT 10;
```

`WHERE` filters rows, `ORDER BY` sorts, `LIMIT` caps the result. SQL clauses are evaluated in a logical order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT.

## Aggregates

```sql
SELECT cohort, COUNT(*) AS students, AVG(score) AS average_score
FROM students
GROUP BY cohort
HAVING COUNT(*) > 1;
```

`WHERE` filters rows before grouping; `HAVING` filters groups after.

## Joins

```sql
SELECT s.name, COUNT(sub.id) AS submissions
FROM students AS s
LEFT JOIN submissions AS sub ON sub.student_id = s.id
GROUP BY s.id, s.name
ORDER BY submissions DESC;
```

`INNER JOIN` keeps only matching pairs. `LEFT JOIN` keeps every left row, filling missing matches with NULL — useful for "students with zero submissions".

## Writing data

```sql
INSERT INTO students (name, cohort, score) VALUES ('Ada', '2026-spring', 91);
UPDATE students SET score = 95 WHERE name = 'Ada';
DELETE FROM students WHERE id = 3;
```

Always include a `WHERE` on UPDATE and DELETE unless you truly mean every row. Run a `SELECT` with the same condition first.

## Normalisation in one paragraph

Store each fact once. A student's name belongs in `students`, not repeated on every submission. If a value changes, one update should be enough. Related facts go in related tables connected by keys.

## Common mistakes

- Storing dates as free text in inconsistent formats.
- Using `SELECT *` in application code and depending on column order.
- Forgetting `WHERE` and deleting everything.
- Encoding lists into comma-separated strings instead of a related table.
- Mixing up NULL (unknown) with 0 or empty string.

## Guided practice

Write a query returning each cohort's highest score. Use `MAX(score)` with `GROUP BY cohort`.

## Summary

Relational databases enforce structure. Keys connect tables, constraints protect data, and SQL expresses exactly which rows you want. Verify destructive statements before running them.

## Further reading

- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [SQLite documentation](https://www.sqlite.org/docs.html)
''',
            "exercises": [
                {
                    "title": "Query the top scores",
                    "description": "Use sqlite3 to read filtered, ordered rows.",
                    "instructions": (
                        "The database already contains a students table with "
                        "columns id, name, cohort, and score. Complete "
                        "top_students(connection, minimum) returning a list of "
                        "names with score >= minimum, highest first, ties by name."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def top_students(connection, minimum):\n    pass\n',
                    "solution": 'def top_students(connection, minimum):\n    rows = connection.execute(\n        """\n        SELECT name FROM students\n        WHERE score >= ?\n        ORDER BY score DESC, name ASC\n        """,\n        (minimum,),\n    ).fetchall()\n    return [row[0] for row in rows]\n',
                    "tests": 'import sqlite3\n\nconnection = sqlite3.connect(":memory:")\nconnection.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, cohort TEXT, score REAL)")\nconnection.executemany(\n    "INSERT INTO students (name, cohort, score) VALUES (?, ?, ?)",\n    [("Ada", "a", 95), ("Grace", "a", 88), ("Linus", "b", 95), ("Edsger", "b", 60)],\n)\nassert top_students(connection, 90) == ["Ada", "Linus"]\nassert top_students(connection, 100) == []\nassert top_students(connection, 0)[0] == "Ada"\n',
                    "hints": [
                        "Use a parameter placeholder (?) and pass a tuple.",
                        "Order by score DESC, then name ASC.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "sql", "sqlite"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "python-sqlite-safely",
            "title": "Python, SQLite, and Safe Transactions",
            "description": (
                "Connect from Python, parameterise every query, manage "
                "transactions, and design a small repository layer."
            ),
            "difficulty": "intermediate",
            "minutes": 55,
            "tags": ["python", "sqlite", "sql", "security", "transactions"],
            "objectives": [
                "Use sqlite3 connection and cursor APIs",
                "Prevent SQL injection with parameters",
                "Commit and roll back transactions",
                "Separate SQL access from business logic",
            ],
            "resources": [
                {
                    "title": "sqlite3 — Python tutorial",
                    "url": "https://docs.python.org/3/library/sqlite3.html",
                    "resource_type": "reference",
                },
                {
                    "title": "OWASP — SQL injection",
                    "url": "https://owasp.org/www-community/attacks/SQL_Injection",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Python, SQLite, and Safe Transactions

## Connect and query

```python
import sqlite3

connection = sqlite3.connect("study.db")
connection.row_factory = sqlite3.Row

with connection:
    connection.execute(
        "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL)"
    )
    connection.execute("INSERT INTO notes (body) VALUES (?)", ("first note",))

rows = connection.execute("SELECT id, body FROM notes ORDER BY id").fetchall()
for row in rows:
    print(row["id"], row["body"])

connection.close()
```

`with connection:` commits on success and rolls back on exception. It does **not** close the connection.

## Parameterised queries stop injection

```python
# Never do this
query = f"SELECT * FROM users WHERE email = '{email}'"
```

If `email` contains `' OR '1'='1`, the query changes meaning. Use placeholders:

```python
row = connection.execute(
    "SELECT id, email FROM users WHERE email = ?", (email,)
).fetchone()
```

Placeholders work for values, not for table or column names. Validate identifiers against an allowlist if they must be dynamic.

## Transactions protect multi-step writes

```python
def transfer(connection, from_id, to_id, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    with connection:
        connection.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, from_id),
        )
        connection.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, to_id),
        )
```

If either statement fails, the block rolls back and no money disappears. Commit boundaries are a design decision: group writes that must succeed or fail together.

## A small repository layer

```python
class NoteRepository:
    def __init__(self, connection):
        self.connection = connection

    def add(self, body):
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO notes (body) VALUES (?)", (body,)
            )
        return cursor.lastrowid

    def all(self):
        rows = self.connection.execute("SELECT id, body FROM notes ORDER BY id")
        return [dict(row) for row in rows]
```

Business logic calls `repository.add(...)` instead of writing SQL inline. Tests can use an in-memory database (":memory:").

## Migrations, briefly

Schema changes need a plan: add columns with defaults, backfill, then enforce constraints. Tools such as Alembic automate this for larger projects. Never drop a production column in the same release that stops using it.

## Backups and concurrency

SQLite is excellent for local tools and small services. It allows one writer at a time; for concurrent web workloads, use a server database such as PostgreSQL. Back up before migrations, and test restores, not just backups.

## Common mistakes

- String-formatting SQL.
- Opening a connection per query in a tight loop.
- Forgetting to commit (or committing inside a loop unnecessarily).
- Storing passwords in plain text — hash them with a dedicated library.
- Returning raw database rows to templates without shaping them.

## Guided practice

Why is `cursor.execute("SELECT * FROM t WHERE id = ?", (user_id,))` safer than an f-string even when `user_id` is an integer? Because the habit protects every call site, including ones added later with strings.

## Summary

SQLite gives you real SQL with almost no setup. Parameterise, transact, and wrap database access in a small layer. Keep credentials and production data out of source control.

## Further reading

- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
''',
            "exercises": [
                {
                    "title": "Safe insert with validation",
                    "description": "Combine business rules with parameterised SQL.",
                    "instructions": (
                        "Complete add_student(connection, name, score). Reject an "
                        "empty name or a score outside 0–100 with ValueError. Insert "
                        "using a parameterised query and return the new row id."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def add_student(connection, name, score):\n    pass\n',
                    "solution": 'def add_student(connection, name, score):\n    cleaned = (name or "").strip()\n    if not cleaned:\n        raise ValueError("name is required")\n    if not 0 <= score <= 100:\n        raise ValueError("score must be between 0 and 100")\n    with connection:\n        cursor = connection.execute(\n            "INSERT INTO students (name, score) VALUES (?, ?)",\n            (cleaned, score),\n        )\n    return cursor.lastrowid\n',
                    "tests": 'import sqlite3\n\nconnection = sqlite3.connect(":memory:")\nconnection.execute("CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, score REAL)")\nfirst = add_student(connection, " Ada ", 90)\nassert isinstance(first, int) and first > 0\nrow = connection.execute("SELECT name, score FROM students WHERE id = ?", (first,)).fetchone()\nassert row == ("Ada", 90)\ntry:\n    add_student(connection, "  ", 50)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\ntry:\n    add_student(connection, "Grace", 140)\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\n',
                    "hints": [
                        "Validate before touching the database.",
                        "Return cursor.lastrowid after the insert.",
                    ],
                    "points": 15,
                    "minutes": 18,
                    "tags": ["python", "sqlite", "validation"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 16 Assessment — SQL",
        "description": "Check keys, joins, parameters, and transactions.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What does a primary key guarantee?",
                "options": [("Each row is uniquely identifiable", True), ("Rows are sorted by name", False), ("Every column is indexed", False), ("Values can repeat", False)],
                "explanation": "A primary key uniquely identifies each row.",
            },
            {
                "content": "Which query is safe from SQL injection?",
                "options": [
                    ("execute('SELECT * FROM users WHERE email = ?', (email,))", True),
                    ("execute(f\"SELECT * FROM users WHERE email = '{email}'\")", False),
                    ("execute('SELECT * FROM users WHERE email = ' + email)", False),
                    ("execute('SELECT * FROM users WHERE email = %s' % email)", False),
                ],
                "explanation": "Bound parameters separate SQL from values.",
            },
            {
                "content": "Why does `with connection:` matter for two related writes?",
                "options": [
                    ("It commits together or rolls back together", True),
                    ("It makes queries 10x faster", False),
                    ("It closes the connection", False),
                    ("It prevents SELECT statements", False),
                ],
                "explanation": "Transactions keep multi-step changes consistent.",
            },
            {
                "content": "When is LEFT JOIN appropriate?",
                "options": [
                    ("When you need every row from the left table, even unmatched", True),
                    ("When you want only matching rows", False),
                    ("When tables have no relationship", False),
                    ("Only with three or more tables", False),
                ],
                "explanation": "LEFT JOIN preserves left-side rows with NULLs for missing matches.",
            },
        ],
    },
    "projects": [
        {
            "title": "Database-Backed Study Tracker",
            "description": (
                "Build a small CLI application that records study sessions in "
                "SQLite and reports weekly totals, streaks, and subject strengths."
            ),
            "requirements": (
                "1. Create tables for subjects and sessions with a foreign key.\n"
                "2. Add a session with subject, minutes, and date.\n"
                "3. List sessions filtered by subject and date range.\n"
                "4. Report total minutes per subject for the last seven days.\n"
                "5. Reject invalid durations and unknown subjects.\n"
                "6. Use parameterised queries everywhere and one transaction per "
                "command.\n"
                "7. Include tests against an in-memory database."
            ),
            "difficulty": "medium",
            "is_capstone": False,
            "estimated_duration_hours": 5,
            "skill_tags": ["python", "sql", "sqlite", "testing"],
            "starter_files": {
                "tracker.py": '"""Study session tracker backed by SQLite."""\nimport sqlite3\nfrom datetime import date\n\nSCHEMA = """\nCREATE TABLE IF NOT EXISTS subjects (\n    id INTEGER PRIMARY KEY,\n    name TEXT NOT NULL UNIQUE\n);\nCREATE TABLE IF NOT EXISTS sessions (\n    id INTEGER PRIMARY KEY,\n    subject_id INTEGER NOT NULL REFERENCES subjects(id),\n    minutes INTEGER NOT NULL CHECK (minutes > 0),\n    studied_on TEXT NOT NULL\n);\n"""\n\n\ndef connect(path="study.db"):\n    connection = sqlite3.connect(path)\n    connection.row_factory = sqlite3.Row\n    connection.executescript(SCHEMA)\n    return connection\n\n\ndef add_subject(connection, name):\n    with connection:\n        cursor = connection.execute(\n            "INSERT INTO subjects (name) VALUES (?)", (name.strip(),)\n        )\n    return cursor.lastrowid\n\n\ndef add_session(connection, subject_name, minutes, studied_on=None):\n    # TODO: validate, look up the subject, insert the session\n    raise NotImplementedError\n\n\ndef weekly_report(connection, today=None):\n    # TODO: return total minutes per subject for the last seven days\n    raise NotImplementedError\n',
                "test_tracker.py": "from tracker import add_session, add_subject, connect, weekly_report\n\n\ndef test_add_session_records_minutes():\n    connection = connect(\":memory:\")\n    add_subject(connection, \"Python\")\n    add_session(connection, \"Python\", 30, \"2026-01-01\")\n    row = connection.execute(\"SELECT minutes FROM sessions\").fetchone()\n    assert row[\"minutes\"] == 30\n",
            },
            "rubric": [
                {"criterion": "Schema uses keys and constraints", "points": 20},
                {"criterion": "All queries parameterised", "points": 20},
                {"criterion": "Validation rejects bad input", "points": 20},
                {"criterion": "Weekly report correct across boundaries", "points": 20},
                {"criterion": "In-memory tests pass", "points": 20},
            ],
        },
    ],
}
