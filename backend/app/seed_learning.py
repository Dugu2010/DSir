"""Seed learning content: quizzes (with questions) and capstone projects.

Run: python -m app.seed_learning
Idempotent — skips courses that already have quizzes/projects.
"""

import asyncio
from uuid import uuid4

from sqlalchemy import select

from app.database import async_session_factory
from app.models import (
    Course, Quiz, Question, QuestionOption, QuestionType,
    Project, ExerciseDifficulty,
)


# ── Quiz content (one quiz per course) ──────────────────────────
_QUIZZES = {
    "python-programming": {
        "title": "Python Fundamentals Quiz",
        "description": "Test your knowledge of Python basics, data types, and operators.",
        "questions": [
            {
                "type": "single_choice",
                "content": "What does `print(type(5))` output?",
                "points": 2,
                "options": [
                    ("<class 'int'>", True),
                    ("<class 'float'>", False),
                    ("<class 'str'>", False),
                    ("int", False),
                ],
                "explanation": "5 is an integer literal, so its type is int.",
            },
            {
                "type": "single_choice",
                "content": "Which of the following is a valid Python variable name?",
                "points": 2,
                "options": [
                    ("my_var", True),
                    ("2things", False),
                    ("my-var", False),
                    ("class", False),
                ],
                "explanation": "Variable names can't start with a digit, contain hyphens, or be a keyword.",
            },
            {
                "type": "single_choice",
                "content": "What is the result of `10 // 3`?",
                "points": 2,
                "options": [
                    ("3", True),
                    ("3.333", False),
                    ("4", False),
                    ("1", False),
                ],
                "explanation": "// is floor division, which truncates toward negative infinity.",
            },
            {
                "type": "single_choice",
                "content": "Which of these data types is immutable?",
                "points": 2,
                "options": [
                    ("tuple", True),
                    ("list", False),
                    ("dict", False),
                    ("set", False),
                ],
                "explanation": "Tuples cannot be modified after creation; lists, dicts, and sets can.",
            },
            {
                "type": "true_false",
                "content": "In Python, `5 == \"5\"` evaluates to True.",
                "points": 2,
                "options": [
                    ("True", False),
                    ("False", True),
                ],
                "explanation": "Python does not coerce types in == comparisons — int 5 and str \"5\" are not equal.",
            },
        ],
    },
    "javascript-complete-guide": {
        "title": "JavaScript Fundamentals Quiz",
        "description": "Check your understanding of JS types, operators, and scope.",
        "questions": [
            {
                "type": "single_choice",
                "content": "What does `typeof []` return?",
                "points": 2,
                "options": [
                    ("\"object\"", True),
                    ("\"array\"", False),
                    ("\"undefined\"", False),
                    ("\"list\"", False),
                ],
                "explanation": "Arrays are objects in JavaScript, so typeof returns \"object\".",
            },
            {
                "type": "single_choice",
                "content": "Which keyword declares a block-scoped variable?",
                "points": 2,
                "options": [
                    ("let", True),
                    ("var", False),
                    ("const", False),
                    ("def", False),
                ],
                "explanation": "let (and const) are block-scoped; var is function-scoped.",
            },
            {
                "type": "single_choice",
                "content": "What is the result of `2 + \"2\"`?",
                "points": 2,
                "options": [
                    ("\"22\"", True),
                    ("4", False),
                    ("NaN", False),
                    ("\"4\"", False),
                ],
                "explanation": "When adding a number and a string, JS coerces the number to a string.",
            },
            {
                "type": "single_choice",
                "content": "Which operator performs strict equality?",
                "points": 2,
                "options": [
                    ("===", True),
                    ("==", False),
                    ("=", False),
                    ("!=", False),
                ],
                "explanation": "=== compares value and type without coercion.",
            },
            {
                "type": "true_false",
                "content": "Variables declared with `const` can be reassigned later.",
                "points": 2,
                "options": [
                    ("True", False),
                    ("False", True),
                ],
                "explanation": "const bindings cannot be reassigned after initialization.",
            },
        ],
    },
    "html-css-fundamentals": {
        "title": "HTML & CSS Fundamentals Quiz",
        "description": "Test your knowledge of HTML semantics and CSS layout.",
        "questions": [
            {
                "type": "single_choice",
                "content": "Which tag defines a hyperlink?",
                "points": 2,
                "options": [
                    ("<a>", True),
                    ("<link>", False),
                    ("<href>", False),
                    ("<url>", False),
                ],
                "explanation": "The <a> (anchor) tag creates hyperlinks.",
            },
            {
                "type": "single_choice",
                "content": "What does CSS stand for?",
                "points": 2,
                "options": [
                    ("Cascading Style Sheets", True),
                    ("Creative Style System", False),
                    ("Computer Style Sheets", False),
                    ("Colorful Style Sheets", False),
                ],
                "explanation": "CSS = Cascading Style Sheets.",
            },
            {
                "type": "single_choice",
                "content": "Which CSS property aligns flex items along the main axis?",
                "points": 2,
                "options": [
                    ("justify-content", True),
                    ("align-items", False),
                    ("text-align", False),
                    ("flex-direction", False),
                ],
                "explanation": "justify-content controls main-axis alignment in flexbox.",
            },
            {
                "type": "single_choice",
                "content": "Which of the following is a semantic HTML element?",
                "points": 2,
                "options": [
                    ("<article>", True),
                    ("<div>", False),
                    ("<span>", False),
                    ("<br>", False),
                ],
                "explanation": "<article> conveys meaning; div/span are generic containers.",
            },
            {
                "type": "true_false",
                "content": "The `<div>` element is a semantic element.",
                "points": 2,
                "options": [
                    ("True", False),
                    ("False", True),
                ],
                "explanation": "<div> is a generic container with no semantic meaning.",
            },
        ],
    },
}


# ── Capstone projects ───────────────────────────────────────────
_PROJECTS = {
    "python-programming": {
        "title": "Capstone: CLI Task Manager",
        "description": "Build a command-line task manager that persists tasks to JSON.",
        "requirements": (
            "1. Add, list, complete, and delete tasks\n"
            "2. Priority levels (high/medium/low)\n"
            "3. Persist tasks to a JSON file\n"
            "4. Filter by status and priority\n"
            "5. Due dates with overdue warnings"
        ),
        "skill_tags": ["Python", "Programming", "Backend"],
        "starter_files": {
            "task_manager.py": "import json\n\nclass TaskManager:\n    def __init__(self, filename='tasks.json'):\n        self.filename = filename\n        self.tasks = self.load()\n\n    def load(self):\n        try:\n            with open(self.filename) as f:\n                return json.load(f)\n        except (FileNotFoundError, json.JSONDecodeError):\n            return []\n\n    def save(self):\n        with open(self.filename, 'w') as f:\n            json.dump(self.tasks, f, indent=2)\n\n    def add(self, title, priority='medium'):\n        self.tasks.append({'title': title, 'priority': priority, 'done': False})\n        self.save()\n\n    def complete(self, index):\n        self.tasks[index]['done'] = True\n        self.save()\n",
        },
    },
    "javascript-complete-guide": {
        "title": "Capstone: Weather Dashboard",
        "description": "Build a weather dashboard with search, forecast, and favorites.",
        "requirements": (
            "1. Search for any city\n"
            "2. Display current conditions (temp, humidity, wind)\n"
            "3. Show a 5-day forecast\n"
            "4. Save favorite cities in localStorage\n"
            "5. Loading and error states"
        ),
        "skill_tags": ["JavaScript", "Web Development", "Frontend"],
        "starter_files": {
            "app.js": "// Weather dashboard entry point\nconst API_KEY = 'your_key_here';\n\nasync function getWeather(city) {\n    const res = await fetch(\n        `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&units=metric`\n    );\n    if (!res.ok) throw new Error('City not found');\n    return res.json();\n}\n",
        },
    },
    "html-css-fundamentals": {
        "title": "Capstone: Portfolio Landing Page",
        "description": "Build a responsive portfolio landing page with HTML and CSS.",
        "requirements": (
            "1. Hero section with headline and CTA\n"
            "2. Features/portfolio section (3+ cards)\n"
            "3. Testimonials section\n"
            "4. Contact form\n"
            "5. Fully responsive with Flexbox/Grid"
        ),
        "skill_tags": ["HTML", "CSS", "Web Design"],
        "starter_files": {
            "index.html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"UTF-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n  <title>My Portfolio</title>\n</head>\n<body>\n  <header>Your header here</header>\n  <main>Your content here</main>\n  <footer>Your footer here</footer>\n</body>\n</html>\n",
        },
    },
}


async def seed_learning() -> None:
    async with async_session_factory() as db:
        courses = (await db.execute(select(Course))).scalars().all()
        by_slug = {c.slug: c for c in courses}

        quizzes_created = 0
        for slug, quiz_data in _QUIZZES.items():
            course = by_slug.get(slug)
            if not course:
                continue
            existing = (await db.execute(
                select(Quiz).where(Quiz.course_id == course.id)
            )).scalar_one_or_none()
            if existing:
                continue

            quiz = Quiz(
                id=uuid4(), course_id=course.id, title=quiz_data["title"],
                description=quiz_data["description"], passing_score=70,
                question_count=len(quiz_data["questions"]), display_order=1,
            )
            db.add(quiz)
            await db.flush()

            for qi, qd in enumerate(quiz_data["questions"]):
                q = Question(
                    id=uuid4(), quiz_id=quiz.id,
                    question_type=QuestionType(qd["type"]),
                    content=qd["content"], explanation=qd.get("explanation"),
                    points=qd.get("points", 2), display_order=qi + 1,
                )
                db.add(q)
                await db.flush()
                for oi, (text, is_correct) in enumerate(qd["options"]):
                    db.add(QuestionOption(
                        id=uuid4(), question_id=q.id, content=text,
                        is_correct=is_correct, display_order=oi + 1,
                    ))
            quizzes_created += 1

        projects_created = 0
        for slug, pdata in _PROJECTS.items():
            course = by_slug.get(slug)
            if not course:
                continue
            existing = (await db.execute(
                select(Project).where(Project.course_id == course.id)
            )).scalar_one_or_none()
            if existing:
                continue
            db.add(Project(
                id=uuid4(), course_id=course.id,
                title=pdata["title"], description=pdata["description"],
                requirements=pdata["requirements"],
                difficulty=ExerciseDifficulty.MEDIUM, is_capstone=True,
                skill_tags=pdata["skill_tags"], starter_files=pdata["starter_files"],
            ))
            projects_created += 1

        await db.commit()
        print(f"✓ Seeded {quizzes_created} quizzes, {projects_created} projects")


if __name__ == "__main__":
    asyncio.run(seed_learning())
