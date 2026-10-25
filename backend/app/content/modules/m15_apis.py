"""Module 15 — APIs, HTTP, JSON, and environment variables."""

MODULE = {
    "slug": "apis-http-json",
    "title": "APIs, HTTP, and JSON",
    "description": (
        "Consume real web APIs safely: understand requests and status codes, "
        "parse JSON, handle failures, paginate results, and keep credentials "
        "out of code."
    ),
    "objectives": [
        "Explain HTTP methods and status codes",
        "Call an API with urllib or httpx",
        "Parse nested JSON into Python data",
        "Handle timeouts, errors, and pagination",
        "Keep secrets in environment variables",
    ],
    "estimated_duration_minutes": 120,
    "lessons": [
        {
            "slug": "http-and-json-fundamentals",
            "title": "HTTP and JSON Fundamentals",
            "description": (
                "A request is a question, a status code is an answer, and JSON "
                "is the shared data format in between."
            ),
            "difficulty": "beginner",
            "minutes": 45,
            "tags": ["python", "api", "http", "json"],
            "objectives": [
                "Describe GET, POST, PUT, PATCH, and DELETE",
                "Interpret 2xx, 4xx, and 5xx responses",
                "Read JSON into dictionaries and lists",
            ],
            "resources": [
                {
                    "title": "Python docs — json",
                    "url": "https://docs.python.org/3/library/json.html",
                    "resource_type": "reference",
                },
                {
                    "title": "MDN — HTTP response status codes",
                    "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# HTTP and JSON Fundamentals

## The request/response model

Your program sends an HTTP request to a URL and receives a response with a status code, headers, and a body.

| Method | Typical purpose | Safe to repeat? |
|--------|-----------------|-----------------|
| GET | Read a resource | Yes |
| POST | Create something | Not necessarily |
| PUT | Replace a resource | Yes, if designed that way |
| PATCH | Partially update | Not necessarily |
| DELETE | Remove a resource | Usually |

"Idempotent" means repeating the request has the same effect as doing it once. That matters for retries.

## Status codes worth knowing

- **200** OK, **201** Created, **204** No Content.
- **400** Bad Request — your input is malformed.
- **401** Unauthorized — missing or invalid credentials.
- **403** Forbidden — authenticated but not allowed.
- **404** Not Found.
- **429** Too Many Requests — back off and retry later.
- **500** Server Error — not your fault, but handle it.

Treat every response as untrusted. Check the status before using the body.

## JSON maps to Python naturally

```python
import json

payload = '{"name": "Ada", "skills": ["python", "sql"], "active": true}'
data = json.loads(payload)

print(data["name"])        # Ada
print(data["skills"][1])   # sql
print(data["active"])      # True
```

JSON objects become dictionaries, arrays become lists, strings and numbers map directly, and `true`/`false`/`null` become `True`/`False`/`None`.

Serialising the other way:

```python
print(json.dumps({"score": 91, "passed": True}))
```

## Nested data needs defensive access

```python
def city_of(record):
    address = record.get("address") or {}
    return address.get("city", "unknown")
```

Chained indexing like `record["address"]["city"]` raises `KeyError` when any level is missing. Use `.get()` at boundaries, then validate.

## Environment variables for secrets

Never hardcode tokens:

```python
import os

api_key = os.environ.get("WEATHER_API_KEY")
if not api_key:
    raise RuntimeError("WEATHER_API_KEY is not set")
```

In development, put the value in `.env` and load it with `python-dotenv`. In production, set it in the platform's secret settings. Add `.env` to `.gitignore` before the first commit.

## Common mistakes

- Assuming `response.json()` always works (error pages may return HTML).
- Ignoring status codes and reading `data["results"]` on a 400 response.
- Printing API keys in logs or error messages.
- Treating an empty result as an error.
- Parsing JSON with string slicing.

## Guided practice

Given this response, what Python expression returns the second repository name?

```json
{"items": [{"name": "alpha"}, {"name": "beta"}]}
```

Answer: `data["items"][1]["name"]`.

## Summary

HTTP is a contract of methods, status codes, and bodies. JSON is the common data language. Validate both, and keep credentials in the environment.

## Further reading

- [json](https://docs.python.org/3/library/json.html)
- [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
''',
            "exercises": [
                {
                    "title": "Extract nested API data",
                    "description": "Read a JSON-shaped dictionary without crashing.",
                    "instructions": (
                        "Complete extract_usernames(payload) so it returns the "
                        "'login' value for every user in payload['items'], and an "
                        "empty list when 'items' is missing or None. Skip items "
                        "without a login."
                    ),
                    "type": "code_completion",
                    "difficulty": "easy",
                    "starter": 'def extract_usernames(payload):\n    pass\n',
                    "solution": 'def extract_usernames(payload):\n    items = payload.get("items") or []\n    usernames = []\n    for item in items:\n        login = item.get("login")\n        if login:\n            usernames.append(login)\n    return usernames\n',
                    "tests": 'data = {"items": [{"login": "ada"}, {"login": "grace"}]}\nassert extract_usernames(data) == ["ada", "grace"]\nassert extract_usernames({}) == []\nassert extract_usernames({"items": None}) == []\nassert extract_usernames({"items": [{"login": "x"}, {}]}) == ["x"]\n',
                    "hints": [
                        "Use payload.get('items') or [].",
                        "Skip missing logins with item.get('login').",
                    ],
                    "points": 10,
                    "minutes": 10,
                    "tags": ["python", "api", "json"],
                },
            ],
            "quiz": None,
        },
        {
            "slug": "calling-apis-reliably",
            "title": "Calling APIs Reliably",
            "description": (
                "Timeouts, retries, pagination, rate limits, and the difference "
                "between a transient failure and a bug."
            ),
            "difficulty": "intermediate",
            "minutes": 55,
            "tags": ["python", "api", "httpx", "reliability"],
            "objectives": [
                "Set timeouts and handle network errors",
                "Retry only safe, transient failures",
                "Follow pagination without losing data",
                "Respect rate limits",
            ],
            "resources": [
                {
                    "title": "Python docs — urllib.request",
                    "url": "https://docs.python.org/3/library/urllib.request.html",
                    "resource_type": "reference",
                },
                {
                    "title": "httpx documentation",
                    "url": "https://www.python-httpx.org/",
                    "resource_type": "reference",
                },
            ],
            "content": r'''# Calling APIs Reliably

## Start with the standard library

```python
import json
import urllib.error
import urllib.request


def fetch_json(url, timeout=10):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DSir-learning/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"HTTP {error.code} from {url}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"network error for {url}: {error.reason}") from error
    return json.loads(body)
```

Always set a timeout. Without one, a stalled server can freeze your program indefinitely.

With `httpx`, the shape is similar:

```python
import httpx

response = httpx.get("https://api.example.com/items", timeout=10)
response.raise_for_status()
data = response.json()
```

Install it with `pip install httpx`; it is not part of the standard library.

## Retry the right failures

Retry timeouts, connection errors, 429, and 5xx. Do not retry a 400 or 401: repeating the same invalid request will not help.

```python
import time


def fetch_with_retry(fetch, attempts=3, base_delay=1.0):
    for attempt in range(attempts):
        try:
            return fetch()
        except RuntimeError:
            if attempt == attempts - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))
```

Exponential backoff gives the server room to recover. In real systems, add jitter and respect `Retry-After`.

Never retry a non-idempotent POST blindly unless the API supports an idempotency key.

## Pagination

Most list endpoints return one page at a time:

```python
def all_items(fetch_page):
    page = 1
    while True:
        data = fetch_page(page)
        items = data.get("items") or []
        if not items:
            return
        yield from items
        page += 1
```

Other APIs use cursors or `next` links. Read the documentation rather than guessing. Add a maximum page guard so a broken API cannot loop forever.

## Rate limits and etiquette

- Cache responses you will reuse.
- Send a descriptive `User-Agent`.
- Batch where the API supports it.
- Back off on 429.
- Do not scrape aggressively or bypass limits.

## Test without the network

Wrap the network call in a small function and inject it. Tests can pass a fake that returns canned data or raises a timeout. This is why separating "fetch" from "transform" matters: the transform is easy to test.

```python
def summarise(records):
    return sorted(record["name"] for record in records if record.get("name"))
```

## Common mistakes

- No timeout.
- Retrying forever.
- Logging full headers containing tokens.
- Assuming one page is all the data.
- Parsing floats as currency and losing precision.
- Writing to a database while paginating without deduplicating.

## Guided practice

Why is retrying a 401 three times wasteful? Because the credentials will not change between attempts; the request needs a fix, not repetition.

## Independent practice

Write `fetch_all_pages(fetch_page, max_pages=5)` that collects items and stops on an empty page or the limit. Test it with a fake function.

## Summary

Reliable API clients set timeouts, distinguish permanent from transient failures, back off, paginate carefully, and keep network code separate from logic. Credentials stay in the environment.

## Further reading

- [urllib.request](https://docs.python.org/3/library/urllib.request.html)
- [httpx](https://www.python-httpx.org/)
''',
            "exercises": [
                {
                    "title": "Collect pages safely",
                    "description": "Paginate with a guard against infinite loops.",
                    "instructions": (
                        "Complete collect_pages(fetch_page, max_pages=3). Call "
                        "fetch_page(page_number) starting at 1, extend results with "
                        "the 'items' list, and stop when a page is empty or "
                        "max_pages is reached. Return a flat list."
                    ),
                    "type": "code_completion",
                    "difficulty": "medium",
                    "starter": 'def collect_pages(fetch_page, max_pages=3):\n    pass\n',
                    "solution": 'def collect_pages(fetch_page, max_pages=3):\n    results = []\n    for page_number in range(1, max_pages + 1):\n        data = fetch_page(page_number)\n        items = (data or {}).get("items") or []\n        if not items:\n            break\n        results.extend(items)\n    return results\n',
                    "tests": 'pages = {1: {"items": [1, 2]}, 2: {"items": [3]}, 3: {"items": []}}\nassert collect_pages(lambda n: pages.get(n, {"items": []})) == [1, 2, 3]\ncalls = []\ndef fake(n):\n    calls.append(n)\n    return {"items": [n]}\nassert collect_pages(fake, max_pages=2) == [1, 2]\nassert calls == [1, 2]\nassert collect_pages(lambda n: {"items": []}) == []\n',
                    "hints": [
                        "Loop over range(1, max_pages + 1).",
                        "Break when the items list is empty.",
                    ],
                    "points": 15,
                    "minutes": 15,
                    "tags": ["python", "api", "pagination"],
                },
            ],
            "quiz": None,
        },
    ],
    "quiz": {
        "title": "Module 15 Assessment — APIs",
        "description": "Check status codes, JSON handling, and resilient requests.",
        "passing_score": 70,
        "questions": [
            {
                "content": "Which status code means your request was malformed?",
                "options": [("400", True), ("404", False), ("500", False), ("201", False)],
                "explanation": "400 Bad Request indicates a client-side input problem.",
            },
            {
                "content": "Why should every network request have a timeout?",
                "options": [
                    ("So a stalled server cannot block the program forever", True),
                    ("To make JSON parse faster", False),
                    ("To avoid authentication", False),
                    ("Because HTTP requires it", False),
                ],
                "explanation": "Timeouts turn an indefinite hang into a handled error.",
            },
            {
                "content": "Which failure should generally not be retried unchanged?",
                "options": [("401 Unauthorized", True), ("503 Service Unavailable", False), ("A connection reset", False), ("429 Too Many Requests", False)],
                "explanation": "Invalid credentials need correction, not repetition.",
            },
            {
                "content": "Where should an API token live?",
                "options": [
                    ("In an environment variable or secret store", True),
                    ("Hardcoded in the script", False),
                    ("In a public README", False),
                    ("In a commit message", False),
                ],
                "explanation": "Secrets must never be committed to version control.",
            },
        ],
    },
    "projects": [
        {
            "title": "API-Powered Weather Report",
            "description": (
                "Build a command-line app that fetches current weather for a city "
                "from a public API and prints a readable summary. This project "
                "practises HTTP, JSON, error handling, and secret management."
            ),
            "requirements": (
                "1. Read the API key from an environment variable and fail with a "
                "clear message when missing.\n"
                "2. Accept a city name as a command-line argument.\n"
                "3. Set a request timeout and handle network errors.\n"
                "4. Print temperature, conditions, and humidity.\n"
                "5. Cache the last response in a JSON file and reuse it when the "
                "API fails, clearly labelling cached data.\n"
                "6. Add tests for the response-parsing function using a canned "
                "payload; no network in tests."
            ),
            "difficulty": "medium",
            "is_capstone": False,
            "estimated_duration_hours": 4,
            "skill_tags": ["python", "api", "json", "error-handling", "testing"],
            "starter_files": {
                "weather.py": '"""Fetch and summarise weather for a city."""\nimport json\nimport os\nimport sys\nimport urllib.request\n\nAPI_URL = "https://api.open-meteo.com/v1/forecast"\n\n\ndef build_url(city_latitude, city_longitude):\n    return (\n        f"{API_URL}?latitude={city_latitude}&longitude={city_longitude}"\n        "&current=temperature_2m,relative_humidity_2m"\n    )\n\n\ndef summarise(payload):\n    current = payload.get("current") or {}\n    return {\n        "temperature": current.get("temperature_2m"),\n        "humidity": current.get("relative_humidity_2m"),\n    }\n\n\ndef main():\n    if len(sys.argv) != 2:\n        print("usage: python weather.py <city>")\n        return 1\n    # TODO: geocode the city, fetch the forecast, handle failures, print a summary\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n',
                "test_weather.py": "from weather import summarise\n\n\ndef test_summarise_reads_current_values():\n    payload = {\"current\": {\"temperature_2m\": 21.5, \"relative_humidity_2m\": 60}}\n    assert summarise(payload) == {\"temperature\": 21.5, \"humidity\": 60}\n",
            },
            "rubric": [
                {"criterion": "Correct HTTP request with timeout", "points": 20},
                {"criterion": "Robust JSON parsing and error messages", "points": 20},
                {"criterion": "Key read from environment, never committed", "points": 20},
                {"criterion": "Cached fallback labelled clearly", "points": 20},
                {"criterion": "Parser tests without network access", "points": 20},
            ],
        },
    ],
}
