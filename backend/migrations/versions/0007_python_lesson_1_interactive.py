"""Seed native exercises and a mastery quiz for Python lesson 1.

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
QUIZ_TITLE = "Python Foundations — Lesson 1 Checkpoint"


def get_ids(bind):
    row = bind.execute(sa.text("""
        SELECT l.id, m.id, c.id
        FROM lessons l JOIN modules m ON m.id=l.module_id JOIN courses c ON c.id=m.course_id
        WHERE c.slug=:c AND m.slug=:m AND l.slug=:l LIMIT 1
    """), {"c": COURSE_SLUG, "m": MODULE_SLUG, "l": LESSON_SLUG}).fetchone()
    if not row:
        raise RuntimeError("Python lesson 1 is missing; migration 0005 must run first")
    return row[0], row[1], row[2]


def upgrade() -> None:
    bind = op.get_bind()
    lesson_id, module_id, course_id = get_ids(bind)

    exercises = [
        ("Predict the output", "Predict before running; then compare your prediction with Python.",
         "Write the exact three output lines before running the code.", "output_prediction", "easy",
         'print("DSir")\nprint("Python")\nprint("Foundations")', "DSir\nPython\nFoundations",
         '{"Read top to bottom.","Each print() produces a line."}', '{python,output,prediction}', 3, 5, 1),
        ("Fix the missing parenthesis", "Find the syntax error and make the smallest fix.",
         "Fix the program so it prints both lines.", "debugging", "easy",
         'print("Python is"\nprint("awesome")', 'print("Python is")\nprint("awesome")',
         '{"Check the first print call.","Match every opening parenthesis with a closing one."}', '{python,syntax,debugging}', 4, 5, 2),
        ("Build your first script", "Create a meaningful three-line Python program.",
         "Use exactly three print() statements: your name, that you are learning Python, and something you want to build.", "code_completion", "easy",
         'print("My name is ...")\nprint("I am learning Python")\nprint("I want to build ...")',
         'print("My name is Durgesh")\nprint("I am learning Python")\nprint("I want to build useful software")',
         '{"Use exactly three print() statements.","Change only the text where appropriate."}', '{python,print,programming-basics}', 5, 10, 3),
        ("Choose REPL or script", "Learn when interactive Python and saved scripts are most useful.",
         "Predict the output of this tiny demonstration and explain why a REPL is useful for quick experiments while a .py file is useful for reusable programs.", "output_prediction", "easy",
         'print("REPL: quick experiments")\nprint("Script: saved programs")',
         'REPL: quick experiments\nScript: saved programs',
         '{"Think quick experiment versus reusable program."}', '{python,repl,scripts}', 4, 5, 4),
        ("Change one thing", "Practice the write-run-observe-change cycle.",
         'Change only the text so the output says "Hello, Python!".', "refactoring", "easy",
         'print("Hello")', 'print("Hello, Python!")',
         '{"Keep print().","Only change the string inside the quotes."}', '{python,print,experimentation}', 3, 5, 5),
    ]

    for e in exercises:
        exists = bind.execute(sa.text("SELECT id FROM exercises WHERE lesson_id=:lesson AND title=:title LIMIT 1"),
                              {"lesson": lesson_id, "title": e[0]}).fetchone()
        if exists:
            continue
        bind.execute(sa.text("""
            INSERT INTO exercises
            (lesson_id,course_id,title,description,instructions,exercise_type,difficulty,starter_code,
             solution_code,test_code,hints,skill_tags,estimated_duration_minutes,points,display_order,created_at,updated_at)
            VALUES (:lesson,:course,:title,:description,:instructions,:type,:difficulty,:starter,:solution,
                    NULL,CAST(:hints AS jsonb),CAST(:tags AS text[]),:minutes,:points,:display,now(),now())
        """), {"lesson":lesson_id,"course":course_id,"title":e[0],"description":e[1],"instructions":e[2],
               "type":e[3],"difficulty":e[4],"starter":e[5],"solution":e[6],"hints":e[7],"tags":e[8],
               "minutes":e[9],"points":e[10],"display":e[11]})

    quiz = bind.execute(sa.text("SELECT id FROM quizzes WHERE lesson_id=:lesson AND title=:title LIMIT 1"),
                        {"lesson":lesson_id,"title":QUIZ_TITLE}).fetchone()
    if not quiz:
        quiz = bind.execute(sa.text("""
            INSERT INTO quizzes (lesson_id,module_id,course_id,title,description,passing_score,time_limit_minutes,question_count,display_order,created_at,updated_at)
            VALUES (:lesson,:module,:course,:title,:description,70,8,0,1,now(),now()) RETURNING id
        """), {"lesson":lesson_id,"module":module_id,"course":course_id,"title":QUIZ_TITLE,
               "description":"Mastery checkpoint for programs, Python, execution, output, REPL, scripts, and basic debugging."}).fetchone()
    quiz_id = quiz[0]

    questions = [
        ("What is a program?", "A program is a set of instructions written so a computer can carry out a task.",
         [("A set of instructions for a computer",True),("Only the output on screen",False),("Computer hardware",False),("A Python error",False)]),
        ("What is the difference between source code and output?", "Source code is written by the programmer; output is produced when the program runs.",
         [("Source code is written; output is produced by running it",True),("They are always identical",False),("Output is typed into the editor",False),("Source code exists only after execution",False)]),
        ("What is the REPL especially useful for?", "The REPL gives immediate feedback for quick interactive experiments.",
         [("Quick interactive experiments",True),("Database backups",False),("Replacing every .py file",False),("Installing hardware",False)]),
        ("Why are print() and Print() different?", "Python is case-sensitive, so uppercase and lowercase names can differ.",
         [("Python is case-sensitive",True),("print() is only for numbers",False),("Print() is preferred",False),("They always print different text",False)]),
        ("Which workflow is a strong beginner habit?", "A tight write-run-observe-change loop creates useful feedback.",
         [("Write → run → observe → change → run again",True),("Copy → never run → submit",False),("Change many lines randomly",False),("Ignore errors",False)]),
        ("What should you do when a simple Python error appears?", "Read the error information, inspect the indicated code, fix one thing, and run again.",
         [("Read the error and inspect the indicated code",True),("Delete the program",False),("Change five unrelated lines",False),("Assume the computer is broken",False)]),
    ]

    for index, (content, explanation, options) in enumerate(questions, 1):
        q = bind.execute(sa.text("SELECT id FROM questions WHERE quiz_id=:quiz AND display_order=:display LIMIT 1"),
                         {"quiz":quiz_id,"display":index}).fetchone()
        if q:
            continue
        q = bind.execute(sa.text("""
            INSERT INTO questions (quiz_id,question_type,content,explanation,points,display_order,created_at,updated_at)
            VALUES (:quiz,'single_choice',:content,:explanation,1,:display,now(),now()) RETURNING id
        """), {"quiz":quiz_id,"content":content,"explanation":explanation,"display":index}).fetchone()
        for option_index, (text, correct) in enumerate(options, 1):
            bind.execute(sa.text("""
                INSERT INTO question_options (question_id,content,is_correct,display_order)
                VALUES (:question,:content,:correct,:display)
            """), {"question":q[0],"content":text,"correct":correct,"display":option_index})

    bind.execute(sa.text("UPDATE quizzes SET question_count=(SELECT count(*) FROM questions WHERE quiz_id=:quiz) WHERE id=:quiz"), {"quiz":quiz_id})


def downgrade() -> None:
    bind = op.get_bind()
    quiz = bind.execute(sa.text("SELECT id FROM quizzes WHERE lesson_id IN (SELECT id FROM lessons WHERE slug=:lesson) AND title=:title LIMIT 1"),
                        {"lesson":LESSON_SLUG,"title":QUIZ_TITLE}).fetchone()
    if quiz:
        bind.execute(sa.text("DELETE FROM quizzes WHERE id=:id"), {"id":quiz[0]})
    bind.execute(sa.text("DELETE FROM exercises WHERE lesson_id IN (SELECT id FROM lessons WHERE slug=:lesson) AND title IN (:a,:b,:c,:d,:e)"),
                 {"lesson":LESSON_SLUG,"a":"Predict the output","b":"Fix the missing parenthesis","c":"Build your first script","d":"Choose REPL or script","e":"Change one thing"})
