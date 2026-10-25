"""Module 20 — Portfolio, interviews, and the capstone."""

MODULE = {
    "slug": "portfolio-and-interview-preparation",
    "title": "Portfolio Projects and Interview Preparation",
    "description": (
        "Turn your work into evidence: two or three well-documented projects, "
        "a readable GitHub presence, honest CV language, and structured "
        "practice for entry-level Python interviews."
    ),
    "objectives": [
        "Choose portfolio projects that demonstrate real skills",
        "Document a project for a reviewer",
        "Describe trade-offs clearly",
        "Practise common Python interview formats",
        "Complete a capstone with tests and a README",
    ],
    "estimated_duration_minutes": 130,
    "lessons": [
        {
            "slug": "portfolio-that-gets-read",
            "title": "A Portfolio That Gets Read",
            "description": (
                "Reviewers spend minutes, not hours. Make those minutes count "
                "with a focused README, a live demo or exact run steps, and "
                "evidence of testing."
            ),
            "difficulty": "beginner",
            "minutes": 50,
            "tags": ["python", "career", "portfolio", "documentation"],
            "objectives": [
                "Select projects that show different strengths",
                "Write a README a reviewer can evaluate quickly",
                "Explain trade-offs and limitations honestly",
            ],
            "resources": [
                {
                    "title": "Make a README",
                    "url": "https://www.makeareadme.com/",
                    "resource_type": "reference",
                },
                {
                    "title": "GitHub Docs — About READMEs",
                    "url": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# A Portfolio That Gets Read

## Quality over quantity

Two or three finished projects beat ten abandoned tutorials. Choose projects that demonstrate different abilities:

- A **tool** that solves a real annoyance (file organiser, expense tracker).
- An **API** with validation, tests, and documented endpoints.
- A **data-backed application** with a database and a clear user journey.

Tutorial clones are weak evidence because every candidate has them. A small original project with honest limitations is stronger.

## The five-minute review

A reviewer should be able to answer these quickly:

1. What does it do, in one sentence?
2. How do I run it?
3. What is the most interesting technical decision?
4. Does it work? (tests, screenshots, demo)
5. What would you improve next?

Structure the README in that order.

```markdown
# Study Tracker

A command-line tool that records study sessions in SQLite and prints weekly
totals by subject.

## Run it

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python tracker.py add Python 45
python tracker.py report

## Tests

pytest -q

## Design notes

- SQLite because the data is local and the workload is single-user.
- Parameterised queries throughout; see `repository.py`.
- Weekly boundaries are computed from an injected `today` value so tests are
  deterministic.

## Limitations

- No concurrent writers.
- Reports are text-only.
- No import from other trackers yet.
```

## Show your debugging, not only your success

A short "problems and decisions" section is credible engineering writing:

- Why you chose one approach over another.
- A bug you found and how you fixed it.
- What you would do with more time.

This demonstrates judgement, which is what interviews test.

## Commit history matters

Recruiters and engineers do look. Commit in coherent steps with messages that explain intent. An empty repository with one commit called "final" undermines the code's quality.

## Deploy or provide exact steps

A live link is convenient, but a reproducible local run is sufficient. If deployment is impractical, include a short recording or screenshots of the working app. Never claim a deployment works if you have not tested it yourself.

## Honest language

Say "built a CLI tool that…", not "expert in Python". Avoid claiming years of experience you do not have. Do not list technologies you cannot discuss.

## Common mistakes

- A wall of badges and no explanation.
- Broken setup instructions.
- No tests, or tests that do not run.
- Secrets in the repository.
- Presenting generated tutorial code as original work.
- Screenshots of code instead of the repository link.

## Guided practice

Take your strongest project and write a one-sentence description, then a five-line README skeleton. Ask: could a stranger run this from the README alone?

## Summary

Choose a few original, tested projects. Write for a five-minute review. Document decisions and limitations. Keep history clean. Be precise and honest.

## Further reading

- [Make a README](https://www.makeareadme.com/)
- [About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
''',
            "exercises": [
                {
                    "title": "Write a reviewable project summary",
                    "description": "Practise concise, honest technical writing.",
                    "instructions": (
                        "Complete project_summary(name, features, tests, limitations) "
                        "returning a multi-line string: a '# {name}' heading, a "
                        "'Features:' line with features joined by ', ', a 'Tests:' "
                        "line, and a 'Limitations:' line. Use 'none' when a list is "
                        "empty. End with a newline."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def project_summary(name, features, tests, limitations):\n    pass\n',
                    "solution": 'def project_summary(name, features, tests, limitations):\n    def join(items):\n        return ", ".join(items) if items else "none"\n\n    return (\n        f"# {name}\\n"\n        f"Features: {join(features)}\\n"\n        f"Tests: {join(tests)}\\n"\n        f"Limitations: {join(limitations)}\\n"\n    )\n',
                    "tests": 'text = project_summary("Tracker", ["add", "report"], ["pytest"], [])\nassert text == "# Tracker\\nFeatures: add, report\\nTests: pytest\\nLimitations: none\\n"\nassert project_summary("X", [], [], []) == "# X\\nFeatures: none\\nTests: none\\nLimitations: none\\n"\n',
                    "hints": [
                        "Write a small join helper that handles empty lists.",
                        "Use one f-string per line and join them.",
                    ],
                    "points": 10,
                    "minutes": 10,
                    "tags": ["python", "career", "documentation"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "python-interview-practice",
            "title": "Python Interview Practice",
            "description": (
                "A repeatable structure for technical questions, plus the Python "
                "topics that come up most for entry-level roles."
            ),
            "difficulty": "intermediate",
            "minutes": 80,
            "tags": ["python", "career", "interview", "problem-solving"],
            "objectives": [
                "Use a clear structure when answering coding questions",
                "Explain common Python behaviours accurately",
                "Discuss trade-offs and testing",
                "Ask useful clarifying questions",
            ],
            "resources": [
                {
                    "title": "Python documentation",
                    "url": "https://docs.python.org/3/",
                    "resource_type": "reference",
                },
                {
                    "title": "MIT OCW 6.100L",
                    "url": "https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Python Interview Practice

## A structure for coding questions

1. **Restate** the problem in your own words.
2. **Clarify** inputs, outputs, edge cases, and constraints.
3. **Examples** — work through two by hand.
4. **Plan** — describe the approach before typing.
5. **Implement** in small, named steps.
6. **Test** with normal, boundary, and invalid input.
7. **Reflect** on complexity and what you would change.

Interviewers assess reasoning, communication, and correctness — not typing speed. Silence is harder to evaluate than a stated assumption.

## Clarifying questions that matter

- Can the input be empty?
- Are duplicates allowed?
- Should the result preserve order?
- Is the data sorted?
- How large can the input get?
- What should happen on invalid input?

## Topics that come up repeatedly

**Mutability**
Lists and dictionaries are mutable; strings and tuples are not. A default argument `def add(item, bucket=[])` shares one list across calls. Use `None` and create inside.

**Identity vs equality**
`is` checks identity; `==` checks value. Use `is None`, not `== None`.

**Shallow vs deep copy**
`copy.copy` copies the outer container; nested objects are shared. `copy.deepcopy` copies recursively.

**List comprehensions**
Readable for simple transforms and filters. Nested comprehensions with side effects are not.

**Truthiness**
`0`, `""`, `[]`, `{}`, `set()`, and `None` are falsy. Be explicit when zero is valid.

**Exceptions**
Catch specific exceptions. `except Exception: pass` hides bugs. Use `finally` for cleanup or, better, context managers.

**Generators**
`yield` produces values lazily. Useful for large files and pipelines. A generator can be consumed once.

**Complexity**
Know that list membership is O(n), set/dict membership is average O(1), and sorting is O(n log n).

## A worked example

**Question:** Return the first non-repeating character in a string, or `None`.

Clarify: case-sensitive? whitespace counts? empty string returns `None`.

Plan: count characters, then scan in order. O(n) time, O(k) space.

```python
def first_unique(text):
    counts = {}
    for character in text:
        counts[character] = counts.get(character, 0) + 1
    for character in text:
        if counts[character] == 1:
            return character
    return None
```

Test: `"aab"` → `"b"`, `"aabb"` → `None`, `""` → `None`, `"abc"` → `"a"`.

Then explain the trade-off: a second pass preserves order; using `collections.Counter` is shorter but hides the counting logic if asked to implement it manually.

## Behavioural questions

Use a concrete example with a situation, your action, and the result. For a bug: how you reproduced it, what you changed, and how you verified the fix. Avoid blaming teammates.

## Questions to ask them

- What does a typical first month look like?
- How does the team review code and test changes?
- Which parts of the stack would I work with?
- How is on-call or production support handled?

## Practise out loud

Write code in a plain editor without autocomplete occasionally. Explain each step aloud. Time yourself on one small problem, then review where you hesitated.

## Common mistakes

- Jumping to code before clarifying.
- Ignoring edge cases until the interviewer mentions them.
- Claiming a test passed without running the case.
- Pretending to know something you do not; say how you would find out.
- Over-engineering a simple problem.

## Summary

Interviewing is a skill. Clarify, plan, implement, test, and reflect. Know the language behaviours above, and practise explaining your reasoning.

## Further reading

- [Python documentation](https://docs.python.org/3/)
- [MIT OCW 6.100L](https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/)
''',
            "exercises": [
                {
                    "title": "First unique character",
                    "description": "A classic interview problem with edge cases.",
                    "instructions": (
                        "Complete first_unique(text) returning the first character "
                        "that appears exactly once, preserving order, or None when "
                        "every character repeats or the string is empty. Handle "
                        "spaces and punctuation as ordinary characters."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def first_unique(text):\n    pass\n',
                    "solution": 'def first_unique(text):\n    counts = {}\n    for character in text:\n        counts[character] = counts.get(character, 0) + 1\n    for character in text:\n        if counts[character] == 1:\n            return character\n    return None\n',
                    "tests": 'assert first_unique("aab") == "b"\nassert first_unique("abc") == "a"\nassert first_unique("aabb") is None\nassert first_unique("") is None\nassert first_unique("a b a") == "b"\nassert first_unique("!!") is None\n',
                    "hints": [
                        "Count every character first.",
                        "Scan the original string in order to find the first count of one.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "interview", "problem-solving"],
                },
                {
                    "title": "Explain mutability",
                    "description": "Predict the output of a shared-default bug.",
                    "instructions": (
                        "Complete append_to(item, bucket=None) so each call without "
                        "a bucket starts a new list. Return the list after appending."
                    ),
                    "type": "bug_fixing",
                    "difficulty": "easy",
                    "starter": 'def append_to(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n',
                    "solution": 'def append_to(item, bucket=None):\n    if bucket is None:\n        bucket = []\n    bucket.append(item)\n    return bucket\n',
                    "tests": 'assert append_to("a") == ["a"]\nassert append_to("b") == ["b"]\nshared = ["x"]\nassert append_to("y", shared) == ["x", "y"]\nassert shared == ["x", "y"]\n',
                    "hints": [
                        "The default list is created once, at function definition time.",
                        "Use None as the default and create a list inside.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "interview", "mutability"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 20 Assessment — Career Readiness",
        "description": "Check portfolio, interview, and professional judgement.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Which portfolio project is strongest evidence?",
                "options": [
                    ("A small original tool with tests and a clear README", True),
                    ("A copied tutorial with no changes", False),
                    ("A folder of screenshots", False),
                    ("An empty repository named 'portfolio'", False),
                ],
                "explanation": "Original work with verification and explanation shows real ability.",
            },
            {
                "content": "What should you do first in a coding interview question?",
                "options": [
                    ("Clarify inputs, outputs, and edge cases", True),
                    ("Start typing immediately", False),
                    ("Ask for the answer", False),
                    ("Optimise before understanding", False),
                ],
                "explanation": "Clarifying prevents solving the wrong problem.",
            },
            {
                "content": "What is the result of calling a function with a mutable default argument twice?",
                "options": [
                    ("The default object is shared between calls", True),
                    ("A new default is created each call", False),
                    ("Python raises an error", False),
                    ("The default is copied deeply", False),
                ],
                "explanation": "Defaults are evaluated once when the function is defined.",
            },
            {
                "content": "How should you describe a limitation in a README?",
                "options": [
                    ("Honestly, with the impact and a possible next step", True),
                    ("Hide it", False),
                    ("Claim it is a feature", False),
                    ("Blame the framework", False),
                ],
                "explanation": "Honest limitations build trust and show judgement.",
            },
        ],
    },
    "projects": [
        {
            "title": "Capstone: Personal Learning Tracker",
            "description": (
                "Build and ship a complete application that tracks learning "
                "sessions, supports goals, and exposes a small HTTP API or CLI. "
                "This is your portfolio centrepiece."
            ),
            "requirements": (
                "1. A clear problem statement and intended user in the README.\n"
                "2. Persistent storage (SQLite or a documented JSON store).\n"
                "3. At least five user-facing operations with validation.\n"
                "4. A report: weekly totals, streaks, or topic strengths.\n"
                "5. Automated tests covering core logic and failure paths.\n"
                "6. Configuration through environment variables; no secrets in Git.\n"
                "7. A documented run command that works from a clean checkout.\n"
                "8. Known limitations and next steps listed honestly.\n"
                "9. At least one code review pass: read your own diff and fix naming "
                "and duplication issues."
            ),
            "difficulty": "hard",
            "is_capstone": True,
            "estimated_duration_hours": 20,
            "skill_tags": ["python", "portfolio", "sqlite", "testing", "documentation"],
            "starter_files": {
                "README.md": "# Personal Learning Tracker\n\n## Problem\n\nDescribe the learner you are building for and the problem you solve.\n\n## Run\n\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\npython -m tracker --help\n```\n\n## Design decisions\n\n- Storage choice and why.\n- How validation works.\n- How tests isolate state.\n\n## Limitations\n\n- List real limits, not humblebrags.\n",
                "tracker/__init__.py": '"""Personal learning tracker."""\n\n__version__ = "0.1.0"\n',
                "tracker/__main__.py": '"""Command-line entry point."""\nimport argparse\n\n\ndef build_parser():\n    parser = argparse.ArgumentParser(prog="tracker")\n    sub = parser.add_subparsers(dest="command", required=True)\n    sub.add_parser("report")\n    add = sub.add_parser("add")\n    add.add_argument("topic")\n    add.add_argument("minutes", type=int)\n    return parser\n\n\ndef main(argv=None):\n    args = build_parser().parse_args(argv)\n    # TODO: implement commands with persistent storage\n    print(f"command={args.command}")\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n',
                "tests/test_tracker.py": "def test_placeholder():\n    assert True\n",
            },
            "rubric": [
                {"criterion": "Problem and user clearly stated", "points": 10},
                {"criterion": "Persistence with validated operations", "points": 25},
                {"criterion": "Reporting logic is correct and tested", "points": 20},
                {"criterion": "Tests cover failures as well as success", "points": 20},
                {"criterion": "README lets a stranger run it", "points": 15},
                {"criterion": "Limitations and next steps are honest", "points": 10},
            ],
        },
    ],
}
