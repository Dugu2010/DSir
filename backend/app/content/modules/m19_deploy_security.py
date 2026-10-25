"""Module 19 — Application quality, deployment, and security."""

MODULE = {
    "slug": "shipping-secure-applications",
    "title": "Shipping Secure, Documented Applications",
    "description": (
        "Prepare an application for real users: layered tests, useful "
        "documentation, repeatable deployment, configuration hygiene, and the "
        "security basics that prevent avoidable breaches."
    ),
    "objectives": [
        "Design a practical test pyramid",
        "Write a README and runbook others can follow",
        "Separate configuration from code",
        "Apply authentication, authorisation, and input-safety basics",
        "Deploy with a rollback plan",
    ],
    "estimated_duration_minutes": 110,
    "lessons": [
        {
            "slug": "test-strategy-and-documentation",
            "title": "Test Strategy, Documentation, and Runbooks",
            "description": (
                "What to test at which level, and how to document a project so a "
                "stranger can run it without asking you."
            ),
            "difficulty": "intermediate",
            "minutes": 50,
            "tags": ["python", "testing", "documentation", "quality"],
            "objectives": [
                "Distinguish unit, integration, and end-to-end tests",
                "Choose what to test at each layer",
                "Write a README with setup, usage, and limits",
                "Create a short operational runbook",
            ],
            "resources": [
                {
                    "title": "pytest documentation",
                    "url": "https://docs.pytest.org/en/stable/",
                    "resource_type": "reference",
                },
                {
                    "title": "Make a README",
                    "url": "https://www.makeareadme.com/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Test Strategy, Documentation, and Runbooks

## The test pyramid, practically

- **Unit tests** — pure functions, validation, parsing. Fast, numerous.
- **Integration tests** — database repositories, HTTP clients, file I/O. Slower, fewer.
- **End-to-end tests** — a real user journey through the running stack. Slowest, fewest.

A project with only end-to-end tests is slow and flaky. A project with only unit tests can still fail in production because the pieces do not connect. Use each layer for what it verifies well.

## What deserves a test

- Money, permissions, dates, and data migrations.
- Parsing external input.
- Code paths that broke before.
- Business rules a customer would notice.

A quick heuristic: if a bug here would be embarrassing or expensive, test it.

## Test data and isolation

- Use a fresh in-memory or temporary database per test.
- Never run tests against production.
- Control time and randomness with injected values.
- Clean up temporary files with `tmp_path` or `TemporaryDirectory`.

```python
def test_repository_starts_empty(tmp_path):
    database = tmp_path / "test.db"
    repository = NoteRepository(connect(database))
    assert repository.all() == []
```

## A README that works

A useful README answers:

1. What is this?
2. What does it need? (Python version, database, keys)
3. How do I run it locally?
4. How do I run the tests?
5. What are the known limitations?
6. Where do I report problems?

```markdown
## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

Tests: `pytest -q`
```

Document the working command, not an aspirational one. If setup needs a step, write it down.

## Document decisions, not just features

A short architecture note explaining why SQLite, why a particular framework, and what was deliberately left out saves future maintainers hours. Keep it current or delete it; stale docs are worse than none.

## Runbook essentials

For anything deployed:

- How to check health.
- Where logs live.
- How to restart.
- How to roll back.
- Who to contact.
- Known failure modes and first checks.

Write it before the incident, not during it.

## Common mistakes

- Tests that need a manually prepared database.
- README commands that assume an unstated working directory.
- Screenshots instead of copyable commands.
- No documented environment variables.
- Claiming a feature works without running it.

## Guided practice

Which layer should test "a duplicate email returns 409"? An integration or endpoint test, because the rule depends on persistence and HTTP mapping.

## Summary

Test at the lowest layer that can catch the bug. Document setup and operations with copyable commands. Be explicit about limitations.

## Further reading

- [pytest](https://docs.pytest.org/en/stable/)
- [Make a README](https://www.makeareadme.com/)
''',
            "exercises": [
                {
                    "title": "Classify the tests",
                    "description": "Choose the right layer for each concern.",
                    "instructions": (
                        "Complete classify(description) returning 'unit', "
                        "'integration', or 'end_to_end' using these rules: "
                        "descriptions containing 'browser' or 'full journey' are "
                        "end_to_end; those containing 'database', 'http', or "
                        "'filesystem' are integration; everything else is unit. "
                        "Check end_to_end first, then integration."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def classify(description):\n    pass\n',
                    "solution": 'def classify(description):\n    text = description.lower()\n    if "browser" in text or "full journey" in text:\n        return "end_to_end"\n    if "database" in text or "http" in text or "filesystem" in text:\n        return "integration"\n    return "unit"\n',
                    "tests": 'assert classify("Validate an email address") == "unit"\nassert classify("Repository saves to the database") == "integration"\nassert classify("Sign in through the browser") == "end_to_end"\nassert classify("Full journey from signup to lesson") == "end_to_end"\nassert classify("Fetch from an HTTP API") == "integration"\n',
                    "hints": [
                        "Lowercase the description first.",
                        "Check the end-to-end keywords before integration keywords.",
                    ],
                    "points": 10,
                    "minutes": 8,
                    "tags": ["python", "testing", "quality"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "configuration-deployment-and-security",
            "title": "Configuration, Deployment, and Security Basics",
            "description": (
                "Twelve-factor style configuration, safe defaults, password "
                "hashing, authorisation checks, and a deployment you can undo."
            ),
            "difficulty": "intermediate",
            "minutes": 60,
            "tags": ["python", "security", "deployment", "configuration"],
            "objectives": [
                "Load configuration from the environment",
                "Hash passwords with a dedicated library",
                "Distinguish authentication from authorisation",
                "Plan deployment and rollback steps",
            ],
            "resources": [
                {
                    "title": "OWASP Top 10",
                    "url": "https://owasp.org/www-project-top-ten/",
                    "resource_type": "reference",
                },
                {
                    "title": "The Twelve-Factor App — Config",
                    "url": "https://12factor.net/config",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Configuration, Deployment, and Security Basics

## Configuration lives outside the code

```python
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    debug: bool = False


def load_settings() -> Settings:
    database_url = os.environ.get("DATABASE_URL")
    jwt_secret = os.environ.get("JWT_SECRET")
    if not database_url or not jwt_secret:
        raise RuntimeError("DATABASE_URL and JWT_SECRET are required")
    return Settings(
        database_url=database_url,
        jwt_secret=jwt_secret,
        debug=os.environ.get("DEBUG", "false").lower() == "true",
    )
```

Fail fast when required configuration is missing. Never ship a default production secret; a hardcoded fallback becomes a vulnerability the moment someone deploys without setting the variable.

## Passwords are hashed, never encrypted or stored

```python
from argon2 import PasswordHasher

hasher = PasswordHasher()


def hash_password(raw: str) -> str:
    return hasher.hash(raw)


def verify_password(stored: str, raw: str) -> bool:
    try:
        return hasher.verify(stored, raw)
    except Exception:
        return False
```

Use Argon2id or bcrypt through a maintained library. Do not write your own hashing, and never log passwords or tokens.

## Authentication vs authorisation

- **Authentication** answers "who are you?" — login, tokens, sessions.
- **Authorisation** answers "may you do this?" — roles, ownership, scopes.

Both are required. An authenticated user must still be checked against the resource:

```python
def get_note(note_id: int, user_id: int):
    note = repository.find(note_id)
    if note is None:
        raise NotFound()
    if note.owner_id != user_id:
        raise Forbidden()
    return note
```

Returning 404 instead of 403 for private resources can avoid leaking existence, but be consistent and document the choice.

## Input, output, and dependencies

- Validate input at the boundary with typed models.
- Escape output in HTML contexts; frameworks usually do this, raw HTML does not.
- Parameterise SQL.
- Keep dependencies updated and review lockfile changes.
- Do not expose stack traces, SQL, or internal paths to users.

## Secrets and logs

- Secrets in environment variables or a secret manager.
- `.env` in `.gitignore`, with `.env.example` documenting names only.
- Logs must not contain tokens, passwords, full card numbers, or personal data you do not need.
- Rotate a secret immediately if it is exposed; removing the commit is not enough.

## Deployment checklist

1. Tests pass locally and in CI.
2. Migrations run forward and have a rollback plan.
3. Environment variables are set for the target environment.
4. Health endpoint responds.
5. Logs are structured and reachable.
6. Static assets and CORS origins are correct.
7. A backup exists for destructive migrations.
8. Rollback steps are written down.

Deploy the smallest change you can verify. Watch errors after release. A successful deploy command is not proof that the application works for users.

## Common mistakes

- `DEBUG=true` in production.
- Wildcard CORS with credentials.
- Trusting a user ID from the request body for ownership.
- Committing secrets then deleting the commit (the history still has them).
- Running migrations without a backup.
- Assuming HTTPS everywhere without checking redirects and mixed content.

## Guided practice

A user changes `/notes/5` to `/notes/6` and sees another user's note. Which control failed? Authorisation — the endpoint trusted the path ID without checking ownership.

## Summary

Configuration comes from the environment, secrets never enter Git, passwords are hashed, and every private action checks authorisation. Deploy with a checklist and a rollback path.

## Further reading

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Twelve-Factor App](https://12factor.net/config)
''',
            "exercises": [
                {
                    "title": "Safe configuration loader",
                    "description": "Read settings without insecure defaults.",
                    "instructions": (
                        "Complete load_config(env) where env is a mapping. Require "
                        "DATABASE_URL and SECRET_KEY (raise ValueError if missing or "
                        "blank). Return a dict with database_url, secret_key, and "
                        "debug (True only when DEBUG equals 'true', case-insensitive)."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def load_config(env):\n    pass\n',
                    "solution": 'def load_config(env):\n    database_url = (env.get("DATABASE_URL") or "").strip()\n    secret_key = (env.get("SECRET_KEY") or "").strip()\n    if not database_url or not secret_key:\n        raise ValueError("DATABASE_URL and SECRET_KEY are required")\n    debug = (env.get("DEBUG") or "").strip().lower() == "true"\n    return {\n        "database_url": database_url,\n        "secret_key": secret_key,\n        "debug": debug,\n    }\n',
                    "tests": 'config = load_config({"DATABASE_URL": "sqlite://", "SECRET_KEY": "abc", "DEBUG": "TRUE"})\nassert config == {"database_url": "sqlite://", "secret_key": "abc", "debug": True}\nassert load_config({"DATABASE_URL": "x", "SECRET_KEY": "y"})["debug"] is False\nfor bad in [({},), ({"DATABASE_URL": "x"},), ({"DATABASE_URL": " ", "SECRET_KEY": "y"},)]:\n    try:\n        load_config(*bad)\n        raise AssertionError("expected ValueError")\n    except ValueError:\n        pass\n',
                    "hints": [
                        "Use env.get and treat missing as empty.",
                        "Compare the lowercased DEBUG value to 'true'.",
                    ],
                    "points": 10,
                    "minutes": 10,
                    "tags": ["python", "security", "configuration"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 19 Assessment — Shipping Safely",
        "description": "Check test layers, configuration, and security controls.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Which test layer is usually fastest?",
                "options": [("Unit", True), ("Integration", False), ("End-to-end", False), ("Manual browser testing", False)],
                "explanation": "Pure-function tests avoid I/O and run in milliseconds.",
            },
            {
                "content": "Where should a production secret live?",
                "options": [
                    ("In the platform's environment or secret store", True),
                    ("In settings.py", False),
                    ("In the README", False),
                    ("In a test fixture", False),
                ],
                "explanation": "Secrets must stay out of source control and code.",
            },
            {
                "content": "A signed-in user requests another user's note by ID. What should be checked?",
                "options": [
                    ("Authorisation: whether this user owns the note", True),
                    ("Only whether the user is signed in", False),
                    ("Nothing; IDs are secret", False),
                    ("The note's creation date", False),
                ],
                "explanation": "Authentication does not grant access to every resource.",
            },
            {
                "content": "What belongs in a deployment checklist?",
                "options": [
                    ("Migrations, environment variables, health check, and rollback", True),
                    ("Only the deploy command", False),
                    ("A list of every source file", False),
                    ("The developer's password", False),
                ],
                "explanation": "A release needs verification and a way back.",
            },
        ],
    },
    "projects": [],
}
