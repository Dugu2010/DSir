"""Add native practice and assessment content for Python lesson 1.

Revision ID: 0007_python_lesson_1_interactive
Revises: 0006_fix_python_lesson_1
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_python_lesson_1_interactive"
down_revision: Union[str, None] = "0006_fix_python_lesson_1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COURSE_SLUG = "python"
MODULE_SLUG = "python-foundations"
LESSON_SLUG = "what-is-python-and-how-programs-run"
QUIZ_SLUG = "python-foundations-lesson-1-checkpoint"


def _ids(bind):
    row = bind.execute(
        sa.text(
            """
            SELECT l.id, m.id, c.id
            FROM lessons l
            JOIN modules m ON m.id = l.module_id
            JOIN courses c ON c.id = m.course_id
            WHERE c.slug = :course_slug
              AND m.slug = :module_slug
              AND l.slug = :lesson_slug
            LIMIT 1
            """
        ),
        {
            "course_slug": COURSE_SLUG,
            "module_slug": MODULE_SLUG,
            "lesson_slug": LESSON_SLUG,
        },
    ).fetchone()
    if row is None:
        raise RuntimeError("Python lesson 1 must exist before interactive content can be seeded")
    return row[0], row[1], row[2]


def upgrade() -> None:
    bind = op.get_bind()
    lesson_id, module_id, course_id = _ids(bind)

    # Structured practice: these are real Exercise rows, so the existing
    # practice/submission engine can evaluate them instead of treating them as prose.
    exercises = [
        {
            "title": "Predict the output",
            "description": "Build the habit of predicting a program before running it.",
            "instructions": "Without running the code first, write the exact three lines it will print. Then run it and compare your prediction.",
            "exercise_type": "output_prediction",
            "difficulty": "easy",
            "starter_code": 'print("DSir")\nprint("Python")\nprint("Foundations")',
            "solution_code": 'DSir\nPython\nFoundations',
            "test_code": None,
            "hints": '["Read the print statements from top to bottom.", "Each print() produces its own line."]',
            "skill_tags": '{python,output,prediction}',
            "minutes": 3,
            "points": 5,
            "order": 1,
        },
        {
            "title": "Fix the missing parenthesis",
            "description": "Diagnose a syntax error and make the smallest possible fix.",
            "instructions": "Fix the program so it runs and prints both lines. Do not rewrite the program or add unrelated code.",
            "exercise_type": "debugging",
            "difficulty": "easy",
            "starter_code": 'print("Python is"\nprint("awesome")',
            "solution_code": 'print("Python is")\nprint("awesome")',
            "test_code": 'assert True',
            "hints": '["Look at the first print call.", "Every opening parenthesis needs a matching closing parenthesis."]',
            "skill_tags": '{python,syntax,debugging}',
            "minutes": 4,
            "points": 5,
            "order": 2,
        },
        {
            "title": "Build your first script",
            "description": "Create a small meaningful Python program using only print().",
            "instructions": "Write a program that prints exactly three lines: your name, that you are learning Python, and one thing you want to build with Python.",
            "exercise_type": "code_completion",
            "difficulty": "easy",
            "starter_code": 'print("My name is ...")\nprint("I am learning Python")\nprint("I want to build ...")',
            "solution_code": 'print("My name is Durgesh")\nprint("I am learning Python")\nprint("I want to build useful software")',
            "test_code": None,
            "hints": '["Use exactly three print() statements.", "The text inside quotes is up to you for the first and third lines."]',
            "skill_tags": '{python,print,programming-basics}',
            "minutes": 5,
            "points": 10,
            "order": 3,
        },
        {
            "title": "REPL or script?",
            "description": "Choose the right environment for a situation and explain why.",
            "instructions": "For each situation, decide whether the REPL or a .py script is the better choice: (1) quickly testing what 17 + 25 evaluates to, (2) saving a program you will run tomorrow. Explain each choice in one sentence.",
            "exercise_type": "text",
            "difficulty": "easy",
            "starter_code": None,
            "solution_code": "1) REPL, because it is ideal for a quick interactive experiment. 2) A .py script, because the program can be saved and run again.",
            "test_code": None,
            "hints": '["Think: quick experiment versus reusable program."]',
            "skill_tags": '{python,repl,scripts}',
            "minutes": 4,
            "points": 5,
            "order": 4,
        },
        {
            "title": "Change one thing",
            "description": "Practice the write-run-observe-change cycle.",
            "instructions": "Start with print(\"Hello\"). Change only the text so the output says \"Hello, Python!\". Run it and describe what changed.",
            "exercise_type": "refactoring",
            "difficulty": "easy",
            "starter_code": 'print("Hello")',
            "solution_code": 'print("Hello, Python!")',
            "test_code": None,
            "hints": '["Keep the print() call.", "Only change the string inside the quotes."]',
            "skill_tags": '{python,print,experimentation}',
            "minutes": 3,
            "points": 5,
            "order": 5,
        },
    ]

    for e in exercises:
        exists = bind.execute(
            sa.text(
                "SELECT id FROM exercises WHERE lesson_id = :lesson_id AND title = :title LIMIT 1"
            ),
            {"lesson_id": lesson_id, "title": e["title"]},
        ).fetchone()
        if exists is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO exercises (
                        lesson_id, course_id, title, description, instructions,
                        exercise_type, difficulty, starter_code, solution_code,
                        test_code, hints, skill_tags, estimated_duration_minutes,
                        points, display_order, created_at, updated_at
                    ) VALUES (
                        :lesson_id, :course_id, :title, :description, :instructions,
                        :exercise_type, :difficulty, :starter_code, :solution_code,
                        :test_code, CAST(:hints AS jsonb), CAST(:skill_tags AS text[]),
                        :minutes, :points, :order, now(), now()
                    )
                    """
                ),
                {
                    "lesson_id": lesson_id,
                    "course_id": course_id,
                    **e,
                },
            )

    # One checkpoint quiz, with individually persisted questions/options so the
    # existing quiz UI and submission endpoint can score it normally.
    quiz = bind.execute(
        sa.text(
            "SELECT id FROM quizzes WHERE lesson_id = :lesson_id AND title = :title LIMIT 1"
        ),
        {"lesson_id": lesson_id, "title": "Python Foundations — Lesson 1 Checkpoint"},
    ).fetchone()

    if quiz is None:
        quiz = bind.execute(
            sa.text(
                """
                INSERT INTO quizzes (
                    lesson_id, module_id, course_id, title, description,
                    passing_score, time_limit_minutes, question_count,
                    display_order, created_at, updated_at
                ) VALUES (
                    :lesson_id, :module_id, :course_id,
                    'Python Foundations — Lesson 1 Checkpoint',
                    'A short mastery checkpoint covering programs, Python, execution, output, the REPL, scripts, and basic debugging.',
                    70, 8, 0, 1, now(), now()
                )
                RETURNING id
                """
            ),
            {"lesson_id": lesson_id, "module_id": module_id, "course_id": course_id},
        ).fetchone()

    quiz_id = quiz[0]

    questions = [
        (
            "What is a program?",
            "A program is a set of instructions written so a computer can carry out a task.",
            1,
            1,
            [
                ("A set of instructions for a computer", True, 1),
                ("Only the output shown on screen", False, 2),
                ("A computer's physical hardware", False, 3),
                ("A Python error message", False, 4),
            ],
        ),
        (
            "Which statement best describes the difference between source code and output?",
            "Source code is what the programmer writes; output is a result produced when the program runs.",
            1,
            2,
            [
                ("Source code is written by the programmer; output is produced by running it", True, 1),
                ("They are always exactly the same", False, 2),
                ("Output is what the programmer types into the editor", False, 3),
                ("Source code only exists after the program runs", False, 4),
            ],
        ),
        (
            "What is the REPL especially useful for?",
            "The REPL is useful for quick interactive experiments where you want immediate feedback.",
            1,
            3,
            [
                ("Quick interactive experiments", True, 1),
                ("Storing database backups", False, 2),
                ("Replacing every .py file", False, 3),
                ("Installing computer hardware", False, 4),
            ],
        ),
        (
            "Why are print() and Print() different in Python?",
            "Python is case-sensitive, so uppercase and lowercase letters can produce different names.",
            1,
            4,
            [
                ("Python is case-sensitive", True, 1),
                ("They always have different output", False, 2),
                ("print() is only for numbers", False, 3),
                ("Print() is the preferred spelling", False, 4),
            ],
        ),
        (
            "Which workflow is a strong beginner programming habit?",
            "Writing, running, observing, changing, and running again creates a useful feedback loop.",
            1,
            5,
            [
                ("Write → run → observe → change → run again", True, 1),
                ("Copy → never run → submit", False, 2),
                ("Change many lines randomly → run once", False, 3),
                ("Ignore errors → continue", False, 4),
            ],
        ),
        (
            "When a simple Python error appears, what should you generally do first?",
            "Start by reading the last line of the error and inspecting the file/line Python identifies.",
            1,
            6,
            [
                ("Read the error information and inspect the indicated code", True, 1),
                ("Delete the whole program", False, 2),
                ("Change five unrelated lines", False, 3),
                ("Assume the computer is broken", False, 4),
            ],
        ),
    ]

    for content, explanation, points, order, options in questions:
        existing_q = bind.execute(
            sa.text("SELECT id FROM questions WHERE quiz_id = :quiz_id AND display_order = :display_order LIMIT 1"),
            {"quiz_id": quiz_id, "display_order": order},
        ).fetchone()
        if existing_q is not None:
            continue

        q = bind.execute(
            sa.text(
                """
                INSERT INTO questions (
                    quiz_id, question_type, content, explanation, points,
                    display_order, created_at, updated_at
                ) VALUES (
                    :quiz_id, 'single_choice', :content, :explanation, :points,
                    :display_order, now(), now()
                )
                RETURNING id
                """
            ),
            {
                "quiz_id": quiz_id,
                "content": content,
                "explanation": explanation,
                "points": points,
                "display_order": order,
            },
        ).fetchone()

        for option_content, is_correct, option_order in options:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO question_options (
                        question_id, content, is_correct, display_order
                    ) VALUES (:question_id, :content, :is_correct, :display_order)
                    """
                ),
                {
                    "question_id": q[0],
                    "content": option_content,
                    "is_correct": is_correct,
                    "display_order": option_order,
                },
            )

    bind.execute(
        sa.text(
            "UPDATE quizzes SET question_count = (SELECT count(*) FROM questions WHERE quiz_id = :quiz_id) WHERE id = :quiz_id"
        ),
        {"quiz_id": quiz_id},
    )


def downgrade() -> None:
    bind = op.get_bind()
    quiz = bind.execute(
        sa.text("SELECT id FROM quizzes WHERE lesson_id IN (SELECT id FROM lessons WHERE slug = :lesson_slug) AND title = :title LIMIT 1"),
        {"lesson_slug": LESSON_SLUG, "title": "Python Foundations — Lesson 1 Checkpoint"},
    ).fetchone()
    if quiz is not None:
        bind.execute(sa.text("DELETE FROM quizzes WHERE id = :quiz_id"), {"quiz_id": quiz[0]})

    bind.execute(
        sa.text(
            "DELETE FROM exercises WHERE lesson_id IN (SELECT id FROM lessons WHERE slug = :lesson_slug) AND title IN (:e1, :e2, :e3, :e4, :e5)"
        ),
        {
            "lesson_slug": LESSON_SLUG,
            "e1": "Predict the output",
            "e2": "Fix the missing parenthesis",
            "e3": "Build your first script",
            "e4": "REPL or script?",
            "e5": "Change one thing",
        },
    )
