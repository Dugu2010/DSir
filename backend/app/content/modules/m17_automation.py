"""Module 17 — Automation and practical standard-library usage."""

MODULE = {
    "slug": "automation-and-scripting",
    "title": "Automation, Scripting, and the Standard Library",
    "description": (
        "Write scripts that do real work: walk directories, rename and organise "
        "files, read command-line arguments, parse dates, and schedule safe "
        "recurring jobs."
    ),
    "objectives": [
        "Use pathlib for safe path handling",
        "Build command-line tools with argparse",
        "Parse and format dates with datetime",
        "Automate file operations with dry-run safety",
        "Write logs instead of stray print statements",
    ],
    "estimated_duration_minutes": 115,
    "lessons": [
        {
            "slug": "files-paths-and-command-line-tools",
            "title": "Files, Paths, and Command-Line Tools",
            "description": (
                "From a one-off script to a tool with arguments, validation, and "
                "a dry-run mode that lets you check before you move anything."
            ),
            "difficulty": "intermediate",
            "minutes": 55,
            "tags": ["python", "automation", "pathlib", "argparse", "scripting"],
            "objectives": [
                "Manipulate paths with pathlib",
                "Accept typed command-line arguments",
                "Implement a dry run before destructive changes",
                "Log outcomes clearly",
            ],
            "resources": [
                {
                    "title": "Python docs — pathlib",
                    "url": "https://docs.python.org/3/library/pathlib.html",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — argparse",
                    "url": "https://docs.python.org/3/library/argparse.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Files, Paths, and Command-Line Tools

## pathlib replaces string paths

```python
from pathlib import Path

folder = Path.home() / "Downloads"
for entry in folder.iterdir():
    if entry.is_file() and entry.suffix.lower() == ".pdf":
        print(entry.name, entry.stat().st_size)
```

`Path` handles separators, joins, suffixes, and existence checks. Prefer it to manual string concatenation with `/` or `os.sep`.

```python
target = folder / "reports" / "q1.csv"
target.parent.mkdir(parents=True, exist_ok=True)
```

`exist_ok=True` makes repeated runs safe.

## A command-line interface with argparse

```python
import argparse
from pathlib import Path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="List large files in a folder")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--min-mb", type=float, default=10.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)
```

argparse converts `folder` to `Path` and `min-mb` to `float`, rejects unknown flags, and generates `--help`. Validate semantic rules yourself:

```python
args = parse_args()
if not args.folder.is_dir():
    raise SystemExit(f"not a folder: {args.folder}")
```

## Dry run first

Any script that renames, moves, or deletes files should support a preview:

```python
def plan_moves(folder):
    plans = []
    for path in folder.iterdir():
        if path.is_file():
            destination = folder / "sorted" / path.suffix.lstrip(".") / path.name
            plans.append((path, destination))
    return plans


def apply(plans, dry_run=True):
    for source, destination in plans:
        print(f"{source.name} -> {destination}")
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.replace(destination)
```

Run the preview, read it, then run for real. This single habit prevents most automation disasters.

## Logging beats print

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logging.info("moved %s files", count)
```

Logs include levels and timestamps, can be redirected to a file, and can be filtered. Use `print` for interactive output a user requested; use logging for diagnostics.

## Idempotence

A script is idempotent when running it twice leaves the same result. Skip existing destinations, use `mkdir(exist_ok=True)`, and never append duplicate records without checking.

## Safety rules

- Never delete recursively based on an unchecked variable.
- Resolve and validate the base directory before acting.
- Refuse to operate on `/` or the home directory without an explicit override.
- Keep backups for irreversible operations.
- Test on a temporary directory first (`tempfile.TemporaryDirectory`).

## Common mistakes

- Building paths with string `+`.
- Assuming files have extensions.
- Ignoring permission errors.
- Overwriting files silently.
- Parsing arguments by hand with `sys.argv`.

## Guided practice

Why is `Path("data") / ".." / "secrets.txt"` risky? Because `..` escapes the intended folder. Resolve the path and check it is inside the allowed root before reading or writing.

## Summary

pathlib makes file handling readable, argparse makes tools usable, dry runs make automation safe, and logging makes failures diagnosable.

## Further reading

- [pathlib](https://docs.python.org/3/library/pathlib.html)
- [argparse](https://docs.python.org/3/library/argparse.html)
- [logging HOWTO](https://docs.python.org/3/howto/logging.html)
''',
            "exercises": [
                {
                    "title": "Organise files by extension",
                    "description": "Plan safe moves without touching the disk.",
                    "instructions": (
                        "Complete plan_moves(names) taking a list of file names and "
                        "returning (name, folder) pairs, where folder is the "
                        "lowercase extension without the dot, or 'no-extension'. "
                        "Ignore names starting with a dot. Keep the original order."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def plan_moves(names):\n    pass\n',
                    "solution": 'def plan_moves(names):\n    plans = []\n    for name in names:\n        if name.startswith("."):\n            continue\n        if "." in name[1:]:\n            extension = name.rsplit(".", 1)[1].lower()\n            folder = extension if extension else "no-extension"\n        else:\n            folder = "no-extension"\n        plans.append((name, folder))\n    return plans\n',
                    "tests": 'assert plan_moves(["a.PDF", "b.txt", "notes", ".hidden"]) == [("a.PDF", "pdf"), ("b.txt", "txt"), ("notes", "no-extension")]\nassert plan_moves([]) == []\nassert plan_moves(["archive.tar.gz"]) == [("archive.tar.gz", "gz")]\nassert plan_moves(["trailing."]) == [("trailing.", "no-extension")]\n',
                    "hints": [
                        "Skip names whose first character is a dot.",
                        "Use rsplit('.', 1) and handle an empty extension.",
                    ],
                    "points": 10,
                    "minutes": 12,
                    "tags": ["python", "automation", "pathlib"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "dates-json-and-recurring-jobs",
            "title": "Dates, JSON, and Recurring Jobs",
            "description": (
                "Time zones, ISO dates, durable JSON state, and scripts that can "
                "resume after a crash."
            ),
            "difficulty": "intermediate",
            "minutes": 45,
            "tags": ["python", "automation", "datetime", "json"],
            "objectives": [
                "Parse and format ISO dates",
                "Avoid naive datetime bugs",
                "Persist state atomically in JSON",
                "Design a resumable recurring job",
            ],
            "resources": [
                {
                    "title": "Python docs — datetime",
                    "url": "https://docs.python.org/3/library/datetime.html",
                    "resource_type": "reference",
                },
                {
                    "title": "Python docs — json",
                    "url": "https://docs.python.org/3/library/json.html",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Dates, JSON, and Recurring Jobs

## Store dates in ISO 8601

```python
from datetime import date, datetime, timedelta

today = date.today()
print(today.isoformat())              # 2026-10-24
print(today + timedelta(days=7))      # one week later

moment = datetime.fromisoformat("2026-10-24T14:30:00")
print(moment.strftime("%d %b %Y, %H:%M"))
```

ISO strings sort correctly as text and are unambiguous. Avoid `24/10/2026` in storage; it means different things in different regions.

## Time zones

`datetime.now()` returns a naive local time with no zone. That breaks across servers and daylight-saving changes. Prefer timezone-aware values:

```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
```

Convert for display only. `zoneinfo` provides IANA time zones:

```python
from zoneinfo import ZoneInfo

local = now.astimezone(ZoneInfo("Asia/Kolkata"))
```

## Parsing user input safely

```python
from datetime import datetime

def parse_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("use YYYY-MM-DD") from None
```

`from None` hides the internal exception detail while keeping your message clear.

## Atomic JSON state

A crash during `json.dump` can leave a half-written file. Write to a temporary file and replace:

```python
import json
import os
from pathlib import Path


def save_state(path: Path, state: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2), encoding="utf-8")
    os.replace(temporary, path)
```

`os.replace` is atomic on the same filesystem on all major platforms.

```python
def load_state(path: Path) -> dict:
    if not path.exists():
        return {"processed": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"processed": []}
```

Decide deliberately whether corrupt state should reset, raise, or be backed up. Silent data loss is rarely the right answer.

## Resumable jobs

```python
def run(items, state):
    processed = set(state.get("processed", []))
    for item in items:
        if item in processed:
            continue
        handle(item)
        processed.add(item)
        state["processed"] = sorted(processed)
        save_state(STATE_PATH, state)
```

Saving after each item is slower than saving once, but it survives interruption. For large batches, save every N items and log progress.

## Scheduling

Use the operating system's scheduler (cron, systemd timers, Task Scheduler) rather than an infinite `while True` loop inside your script. The script should do one run, exit with a meaningful status code, and log to a file.

```bash
# crontab: every weekday at 07:30
30 7 * * 1-5 /usr/bin/python3 /home/me/scripts/report.py >> /home/me/logs/report.log 2>&1
```

Set absolute paths; cron's environment and working directory differ from your shell.

## Common mistakes

- Comparing naive and aware datetimes (`TypeError`).
- Using local time for stored timestamps.
- Writing JSON directly over the only copy.
- Assuming the job runs once (overlapping cron runs).
- Ignoring non-zero exit codes.

## Guided practice

Why does an overlapping cron job corrupt shared state? Two runs can read the same snapshot and write conflicting results. Use a lock file or a database transaction with a job identifier.

## Summary

Automation is mostly discipline: ISO dates, aware time zones, atomic writes, resumable state, and an external scheduler. Keep the script small and observable.

## Further reading

- [datetime](https://docs.python.org/3/library/datetime.html)
- [json](https://docs.python.org/3/library/json.html)
''',
            "exercises": [
                {
                    "title": "Days until due",
                    "description": "Use date arithmetic and clear errors.",
                    "instructions": (
                        "Complete days_until(due, today). Both are date objects. "
                        "Return the number of days from today to due (negative if "
                        "overdue). Raise ValueError if due is not a date."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def days_until(due, today):\n    pass\n',
                    "solution": 'from datetime import date, datetime\n\n\ndef days_until(due, today):\n    if not isinstance(due, date) or isinstance(due, datetime):\n        raise ValueError("due must be a date")\n    return (due - today).days\n',
                    "tests": 'from datetime import date, datetime\n\nassert days_until(date(2026, 1, 10), date(2026, 1, 1)) == 9\nassert days_until(date(2026, 1, 1), date(2026, 1, 10)) == -9\nassert days_until(date(2026, 1, 1), date(2026, 1, 1)) == 0\ntry:\n    days_until("2026-01-01", date(2026, 1, 1))\n    raise AssertionError("expected ValueError")\nexcept ValueError:\n    pass\n',
                    "hints": [
                        "Subtracting two dates returns a timedelta.",
                        "Use .days on the result.",
                    ],
                    "points": 10,
                    "minutes": 10,
                    "tags": ["python", "automation", "datetime"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 17 Assessment — Automation",
        "description": "Check paths, arguments, dates, and safe file operations.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Why add a --dry-run flag to a file-organising script?",
                "options": [
                    ("To preview actions before changing anything", True),
                    ("To make it run faster", False),
                    ("To skip validation", False),
                    ("To delete files safely", False),
                ],
                "explanation": "A preview is the cheapest protection against destructive mistakes.",
            },
            {
                "content": "Which date format is best for storage?",
                "options": [("ISO 8601, e.g. 2026-10-24", True), ("24/10/2026", False), ("Oct 24", False), ("1698105600", False)],
                "explanation": "ISO dates are unambiguous and sort correctly.",
            },
            {
                "content": "What makes a JSON state write safer?",
                "options": [
                    ("Write a temporary file, then replace the original", True),
                    ("Call json.dump twice", False),
                    ("Write with print", False),
                    ("Store it in memory only", False),
                ],
                "explanation": "Atomic replacement prevents half-written files.",
            },
            {
                "content": "What is a sign a cron script needs absolute paths?",
                "options": [
                    ("It works by hand but fails from cron", True),
                    ("It prints too much", False),
                    ("It uses pathlib", False),
                    ("It has tests", False),
                ],
                "explanation": "Cron starts in a different directory with a minimal environment.",
            },
        ],
    },
    "projects": [
        {
            "title": "File Organizer with Dry Run",
            "description": (
                "Create a script that sorts a folder's loose files into "
                "extension-based subfolders, with a preview mode and a log."
            ),
            "requirements": (
                "1. Accept a folder path and optional --dry-run flag.\n"
                "2. Group files by lowercase extension, skipping directories.\n"
                "3. Never overwrite an existing file; add a numeric suffix instead.\n"
                "4. Log every planned and completed move.\n"
                "5. Handle permission errors per file without aborting the batch.\n"
                "6. Print a summary: moved, skipped, failed.\n"
                "7. Test the planning function on a temporary directory."
            ),
            "difficulty": "medium",
            "is_capstone": False,
            "estimated_duration_hours": 3,
            "skill_tags": ["python", "automation", "pathlib", "argparse"],
            "starter_files": {
                "organize.py": '"""Sort loose files into extension folders."""\nimport argparse\nimport logging\nfrom pathlib import Path\n\nlogging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")\n\n\ndef plan(folder: Path):\n    # TODO: return a list of (source, destination) pairs\n    raise NotImplementedError\n\n\ndef unique_destination(destination: Path) -> Path:\n    # TODO: add -1, -2, ... before the suffix if the path exists\n    raise NotImplementedError\n\n\ndef main(argv=None):\n    parser = argparse.ArgumentParser(description="Sort files by extension")\n    parser.add_argument("folder", type=Path)\n    parser.add_argument("--dry-run", action="store_true")\n    args = parser.parse_args(argv)\n    if not args.folder.is_dir():\n        parser.error(f"not a folder: {args.folder}")\n    moves = plan(args.folder)\n    # TODO: apply moves unless dry run, log results, print a summary\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n',
                "test_organize.py": "from pathlib import Path\n\nfrom organize import plan\n\n\ndef test_plan_groups_by_extension(tmp_path):\n    (tmp_path / \"a.txt\").write_text(\"a\")\n    (tmp_path / \"b.PDF\").write_text(\"b\")\n    moves = plan(tmp_path)\n    assert (tmp_path / \"a.txt\", tmp_path / \"txt\" / \"a.txt\") in moves\n",
            },
            "rubric": [
                {"criterion": "Dry run produces an accurate plan", "points": 20},
                {"criterion": "No existing file is overwritten", "points": 25},
                {"criterion": "Per-file errors do not abort the batch", "points": 20},
                {"criterion": "Summary and logs are accurate", "points": 15},
                {"criterion": "Planning tests use a temporary directory", "points": 20},
            ],
        },
        {
            "title": "JSON Task Manager with Resumable State",
            "description": (
                "Build a command-line task manager that persists tasks in JSON, "
                "supports priorities and due dates, and survives interruption."
            ),
            "requirements": (
                "1. Commands: add, list, done, remove, and report.\n"
                "2. Store tasks in a JSON file with atomic writes.\n"
                "3. Validate due dates as YYYY-MM-DD and flag overdue tasks.\n"
                "4. Filter lists by status and priority.\n"
                "5. Handle a corrupt file by refusing to overwrite and explaining "
                "the problem.\n"
                "6. Include tests for add, complete, filtering, and atomic save."
            ),
            "difficulty": "medium",
            "is_capstone": False,
            "estimated_duration_hours": 4,
            "skill_tags": ["python", "automation", "json", "argparse", "testing"],
            "starter_files": {
                "tasks.py": '"""A small JSON-backed task manager."""\nimport argparse\nimport json\nimport os\nfrom datetime import date\nfrom pathlib import Path\n\nSTATE = Path("tasks.json")\n\n\ndef load(path=STATE):\n    if not path.exists():\n        return []\n    return json.loads(path.read_text(encoding="utf-8"))\n\n\ndef save(tasks, path=STATE):\n    temporary = path.with_suffix(path.suffix + ".tmp")\n    temporary.write_text(json.dumps(tasks, indent=2), encoding="utf-8")\n    os.replace(temporary, path)\n\n\ndef add_task(tasks, title, priority="medium", due=None):\n    # TODO: validate, create a task dict, append, and return it\n    raise NotImplementedError\n\n\ndef complete_task(tasks, task_id):\n    # TODO: mark the matching task done; raise ValueError if missing\n    raise NotImplementedError\n\n\ndef main(argv=None):\n    parser = argparse.ArgumentParser(description="Manage tasks")\n    sub = parser.add_subparsers(dest="command", required=True)\n    add_parser = sub.add_parser("add")\n    add_parser.add_argument("title")\n    add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")\n    add_parser.add_argument("--due")\n    sub.add_parser("list")\n    done_parser = sub.add_parser("done")\n    done_parser.add_argument("id", type=int)\n    args = parser.parse_args(argv)\n    # TODO: dispatch commands and save changes\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n',
                "test_tasks.py": "import pytest\n\nfrom tasks import add_task, complete_task\n\n\ndef test_add_and_complete():\n    tasks = []\n    task = add_task(tasks, \"Read chapter\", \"high\", \"2026-01-01\")\n    assert task[\"title\"] == \"Read chapter\"\n    assert task[\"done\"] is False\n    complete_task(tasks, task[\"id\"])\n    assert tasks[0][\"done\"] is True\n",
            },
            "rubric": [
                {"criterion": "Commands behave as specified", "points": 25},
                {"criterion": "Validation and clear errors", "points": 20},
                {"criterion": "Atomic JSON persistence", "points": 20},
                {"criterion": "Corrupt file handled without data loss", "points": 15},
                {"criterion": "Tests cover core operations", "points": 20},
            ],
        },
    ],
}
