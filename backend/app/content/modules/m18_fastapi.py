"""Module 18 — Backend development fundamentals with FastAPI."""

MODULE = {
    "slug": "backend-with-fastapi",
    "title": "Backend Development with FastAPI",
    "description": (
        "Build a small, real HTTP API: routes, request models, validation, "
        "dependency injection, error responses, and documentation that stays "
        "true to the code."
    ),
    "objectives": [
        "Explain what a web framework does",
        "Define routes and path/query parameters",
        "Validate request bodies with Pydantic models",
        "Return consistent errors and status codes",
        "Structure an API for testing",
    ],
    "estimated_duration_minutes": 125,
    "lessons": [
        {
            "slug": "routes-requests-and-responses",
            "title": "Routes, Requests, and Responses",
            "description": (
                "Map URLs to functions, read path and query parameters, and "
                "return the right status code."
            ),
            "difficulty": "intermediate",
            "minutes": 55,
            "tags": ["python", "fastapi", "backend", "http"],
            "objectives": [
                "Create a FastAPI app with multiple routes",
                "Use path and query parameters",
                "Return JSON with appropriate status codes",
            ],
            "resources": [
                {
                    "title": "FastAPI documentation",
                    "url": "https://fastapi.tiangolo.com/",
                    "resource_type": "reference",
                },
                {
                    "title": "MDN — HTTP overview",
                    "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Routes, Requests, and Responses

## What a framework gives you

FastAPI handles URL routing, request parsing, validation, response serialisation, and interactive documentation. You write functions; it connects them to HTTP.

```python
from fastapi import FastAPI

app = FastAPI(title="Study API")


@app.get("/health")
def health():
    return {"status": "ok"}
```

Run it with `uvicorn main:app --reload`, then visit `/docs` for generated documentation.

## Path and query parameters

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()
COURSES = {1: {"title": "Python"}, 2: {"title": "SQL"}}


@app.get("/courses/{course_id}")
def get_course(course_id: int):
    course = COURSES.get(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="course not found")
    return course


@app.get("/courses")
def list_courses(limit: int = 10):
    return list(COURSES.values())[:limit]
```

Type hints do real work: `course_id: int` converts and validates the string from the URL. `/courses/abc` returns a 422 automatically.

## Status codes are part of the contract

```python
from fastapi import status


@app.post("/courses", status_code=status.HTTP_201_CREATED)
def create_course(payload: dict):
    ...
```

Use 201 for creation, 204 for successful deletion with no body, 400/422 for bad input, 404 for missing resources, 401/403 for authentication and authorisation, and 500 only for genuine server faults.

## Consistent error shape

```python
raise HTTPException(
    status_code=404,
    detail={"code": "course_not_found", "message": "Course 99 does not exist"},
)
```

Whatever shape you choose, apply it everywhere so clients can handle errors generically.

## Async or sync?

FastAPI supports both. Use `async def` when you await I/O (database drivers, HTTP clients). Use plain `def` for CPU-bound or blocking library calls so FastAPI runs them in a worker thread. Do not block the event loop with `time.sleep` or a synchronous network call inside `async def`.

## CORS and browsers

A browser on another origin needs explicit permission:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

Never use `allow_origins=["*"]` together with credentials. List the origins you actually trust.

## Common mistakes

- Returning dictionaries with inconsistent keys across endpoints.
- Using 200 for everything, including failures.
- Trusting client-supplied IDs for ownership checks.
- Blocking the event loop in async routes.
- Leaving debug tracebacks enabled in production.

## Guided practice

Why does `/courses/abc` produce 422 before your function runs? FastAPI validates the path parameter against the `int` annotation.

## Summary

Routes map URLs to functions. Type hints validate input. Status codes communicate outcomes. Consistent errors and correct async usage make an API predictable.

## Further reading

- [FastAPI](https://fastapi.tiangolo.com/)
- [HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
''',
            "exercises": [
                {
                    "title": "Validate pagination parameters",
                    "description": "Write the pure logic an endpoint depends on.",
                    "instructions": (
                        "Complete page_bounds(limit, offset, total). Return a tuple "
                        "(start, end) clamping the range to the collection. Raise "
                        "ValueError for a negative limit or offset, or a limit above "
                        "100. For total=0 return (0, 0)."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def page_bounds(limit, offset, total):\n    pass\n',
                    "solution": 'def page_bounds(limit, offset, total):\n    if limit < 0 or offset < 0:\n        raise ValueError("limit and offset must be non-negative")\n    if limit > 100:\n        raise ValueError("limit must be at most 100")\n    start = min(offset, total)\n    end = min(offset + limit, total)\n    return start, end\n',
                    "tests": 'assert page_bounds(10, 0, 25) == (0, 10)\nassert page_bounds(10, 20, 25) == (20, 25)\nassert page_bounds(10, 30, 25) == (25, 25)\nassert page_bounds(10, 0, 0) == (0, 0)\nassert page_bounds(0, 5, 10) == (5, 5)\nfor args in [(-1, 0, 10), (10, -1, 10), (101, 0, 10)]:\n    try:\n        page_bounds(*args)\n        raise AssertionError("expected ValueError")\n    except ValueError:\n        pass\n',
                    "hints": [
                        "Validate before computing.",
                        "Clamp start and end to total.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "backend", "validation"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "request-models-and-testing-endpoints",
            "title": "Request Models, Dependencies, and Endpoint Tests",
            "description": (
                "Use Pydantic for validation, a dependency for shared logic, and "
                "TestClient to test real HTTP behaviour without a running server."
            ),
            "difficulty": "intermediate",
            "minutes": 55,
            "tags": ["python", "fastapi", "pydantic", "testing"],
            "objectives": [
                "Define request and response models",
                "Return clear validation failures",
                "Share logic with dependency injection",
                "Test endpoints with TestClient",
            ],
            "resources": [
                {
                    "title": "FastAPI — Testing",
                    "url": "https://fastapi.tiangolo.com/tutorial/testing/",
                    "resource_type": "reference",
                },
                {
                    "title": "Pydantic documentation",
                    "url": "https://docs.pydantic.dev/latest/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Request Models, Dependencies, and Endpoint Tests

## Pydantic models describe the contract

```python
from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    hours: int = Field(gt=0, le=2000)


class CourseRead(BaseModel):
    id: int
    title: str
    level: str
```

```python
@app.post("/courses", response_model=CourseRead, status_code=201)
def create_course(payload: CourseCreate):
    return {"id": next_id(), "title": payload.title, "level": payload.level}
```

`CourseCreate` defines what clients may send. `CourseRead` defines what they get back. Separating the two prevents leaking internal fields such as password hashes or internal flags.

## Validation errors are automatic

Sending `{"title": "x"}` returns 422 with a structured explanation. Do not re-implement validation in the route; let the model do it, then add business rules that a schema cannot express (for example, "title must be unique").

## Dependencies

```python
from fastapi import Depends


def get_current_user(token: str = ""):
    if not token:
        raise HTTPException(status_code=401, detail="authentication required")
    return {"id": 1, "name": "Ada"}


@app.get("/me")
def me(user=Depends(get_current_user)):
    return user
```

Dependencies centralise authentication, database sessions, and pagination defaults. They are also easy to override in tests.

## Testing with TestClient

```python
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_course_rejects_short_title():
    response = client.post("/courses", json={"title": "x", "level": "beginner", "hours": 4})
    assert response.status_code == 422
```

`TestClient` runs the app in-process; no server, no ports, fast tests. It is built on `httpx`.

## Test the contract, not the implementation

Assert status codes, response shapes, and side effects. Avoid asserting on private function calls. Include:

- Success cases.
- Missing and malformed input.
- Authentication and authorisation failures (401, 403).
- Not-found cases.
- One case where two users must not see each other's data.

## Ownership checks

Never trust an ID from the client for access decisions. Load the record and compare its owner to the authenticated user:

```python
if note.owner_id != user["id"]:
    raise HTTPException(status_code=403, detail="not allowed")
```

Otherwise changing an ID in the URL exposes someone else's data.

## Common mistakes

- Using the request model as the response model, leaking internal fields.
- Catching validation errors and returning 200.
- Testing only the happy path.
- Sharing mutable global state across tests.
- Using a real production database in tests.

## Guided practice

Why is a 403 different from a 401? 401 means the identity is missing or invalid; 403 means the identity is known but lacks permission.

## Summary

Pydantic models make input and output explicit. Dependencies share logic cleanly. TestClient verifies real HTTP behaviour quickly. Check ownership on every private resource.

## Further reading

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic](https://docs.pydantic.dev/latest/)
''',
            "exercises": [
                {
                    "title": "Validate a course payload without a framework",
                    "description": "Write schema-style validation you can unit test.",
                    "instructions": (
                        "Complete validate_course(payload) returning a cleaned dict "
                        "with title, level, and hours. Strip the title; require "
                        "3–120 characters. Level must be beginner, intermediate, or "
                        "advanced. Hours must be an integer from 1 to 2000. Raise "
                        "ValueError with a clear message otherwise."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def validate_course(payload):\n    pass\n',
                    "solution": 'def validate_course(payload):\n    title = str(payload.get("title", "")).strip()\n    if not 3 <= len(title) <= 120:\n        raise ValueError("title must be 3-120 characters")\n    level = payload.get("level")\n    if level not in {"beginner", "intermediate", "advanced"}:\n        raise ValueError("invalid level")\n    hours = payload.get("hours")\n    if not isinstance(hours, int) or isinstance(hours, bool) or not 1 <= hours <= 2000:\n        raise ValueError("hours must be an integer from 1 to 2000")\n    return {"title": title, "level": level, "hours": hours}\n',
                    "tests": 'assert validate_course({"title": "  Python  ", "level": "beginner", "hours": 10}) == {"title": "Python", "level": "beginner", "hours": 10}\nfor bad in [\n    {"title": "ab", "level": "beginner", "hours": 10},\n    {"title": "Python", "level": "expert", "hours": 10},\n    {"title": "Python", "level": "beginner", "hours": 0},\n    {"title": "Python", "level": "beginner", "hours": 2001},\n    {"title": "Python", "level": "beginner", "hours": "10"},\n]:\n    try:\n        validate_course(bad)\n        raise AssertionError(f"expected ValueError for {bad}")\n    except ValueError:\n        pass\n',
                    "hints": [
                        "Validate types before ranges.",
                        "Remember bool is a subclass of int in Python.",
                    ],
                    "points": 15,
                    "minutes": 18,
                    "tags": ["python", "backend", "validation", "pydantic"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 18 Assessment — FastAPI",
        "description": "Check routing, validation, status codes, and endpoint tests.",
        "passing_score": 70,
        "questions": [
            {
                "content": "What does FastAPI do with a path parameter annotated as int?",
                "options": [
                    ("Converts and validates it, rejecting non-integers", True),
                    ("Ignores the annotation", False),
                    ("Stores it as a string", False),
                    ("Sends it to the database", False),
                ],
                "explanation": "Type hints drive conversion and validation.",
            },
            {
                "content": "Which status code should a successful creation return?",
                "options": [("201", True), ("200", False), ("204", False), ("302", False)],
                "explanation": "201 Created communicates that a new resource exists.",
            },
            {
                "content": "Why use separate request and response models?",
                "options": [
                    ("To avoid leaking internal fields and to make the contract explicit", True),
                    ("Because Python requires it", False),
                    ("To double the code", False),
                    ("To skip validation", False),
                ],
                "explanation": "Response models control exactly what leaves the server.",
            },
            {
                "content": "What does FastAPI's TestClient need to test endpoints?",
                "options": [
                    ("No running server; it calls the app in-process", True),
                    ("A deployed production server", False),
                    ("A browser", False),
                    ("A paid account", False),
                ],
                "explanation": "TestClient exercises the ASGI app directly and quickly.",
            },
        ],
    },
    "projects": [
        {
            "title": "FastAPI Study Notes API",
            "description": (
                "Build a small authenticated notes API with validation, "
                "ownership checks, and a tested endpoint suite."
            ),
            "requirements": (
                "1. Endpoints to create, list, read, update, and delete notes.\n"
                "2. Pydantic models for create/update and a separate response model.\n"
                "3. An in-memory store or SQLite repository; keep it swappable.\n"
                "4. Reject empty titles and bodies over 10,000 characters.\n"
                "5. Return 404 for missing notes and 403 when a note belongs to "
                "another user.\n"
                "6. Use a dependency for the current user.\n"
                "7. Tests with TestClient covering success, validation, 404, 403, "
                "and deletion."
            ),
            "difficulty": "hard",
            "is_capstone": False,
            "estimated_duration_hours": 6,
            "skill_tags": ["python", "fastapi", "backend", "testing", "validation"],
            "starter_files": {
                "main.py": '"""Study notes API."""\nfrom fastapi import Depends, FastAPI, HTTPException, status\nfrom pydantic import BaseModel, Field\n\napp = FastAPI(title="Study Notes API")\n\n\nclass NoteCreate(BaseModel):\n    title: str = Field(min_length=1, max_length=120)\n    body: str = Field(min_length=1, max_length=10_000)\n\n\nclass NoteRead(NoteCreate):\n    id: int\n    owner_id: int\n\n\nNOTES: dict[int, dict] = {}\nNEXT_ID = 1\n\n\ndef get_current_user():\n    # Replace with real authentication in production.\n    return {"id": 1}\n\n\n@app.get("/notes", response_model=list[NoteRead])\ndef list_notes(user=Depends(get_current_user)):\n    return [note for note in NOTES.values() if note["owner_id"] == user["id"]]\n\n\n@app.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)\ndef create_note(payload: NoteCreate, user=Depends(get_current_user)):\n    # TODO: allocate an id, store the note with owner_id, return it\n    raise NotImplementedError\n',
                "test_main.py": "from fastapi.testclient import TestClient\n\nfrom main import app\n\nclient = TestClient(app)\n\n\ndef test_list_notes_starts_empty():\n    response = client.get(\"/notes\")\n    assert response.status_code == 200\n    assert response.json() == []\n",
            },
            "rubric": [
                {"criterion": "CRUD endpoints behave correctly", "points": 25},
                {"criterion": "Models enforce length and required fields", "points": 20},
                {"criterion": "Ownership enforced on read, update, and delete", "points": 25},
                {"criterion": "Correct status codes, including 404 and 403", "points": 15},
                {"criterion": "TestClient suite covers happy and failure paths", "points": 15},
            ],
        },
    ],
}
