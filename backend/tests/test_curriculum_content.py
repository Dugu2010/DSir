"""Content integrity checks for the authored Python curriculum.

These tests do not need a database. They verify that:
* every module, lesson, exercise, and quiz question is structurally complete;
* identifiers are unique;
* every quiz question has at least one correct option;
* every exercise's reference solution passes its own tests.

The reference solutions are executed in a subprocess with a timeout so a bad
solution cannot hang the test suite. Only the Python standard library is
required; that matches the Pyodide sandbox used by the app.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from app.content.modules import MODULES, PROJECTS

EXERCISES = [
    (module, lesson, exercise)
    for module in MODULES
    for lesson in module["lessons"]
    for exercise in lesson["exercises"]
]


def test_course_has_twenty_modules():
    assert len(MODULES) >= 20
    slugs = [module["slug"] for module in MODULES]
    assert len(slugs) == len(set(slugs))


def test_every_module_is_structurally_complete():
    for module in MODULES:
        assert module["title"].strip()
        assert module["description"].strip()
        assert module["objectives"]
        assert module["estimated_duration_minutes"] > 0
        assert len(module["lessons"]) >= 1
        quiz = module["quiz"]
        assert quiz["title"].strip()
        assert quiz["questions"]
        for question in quiz["questions"]:
            assert question["content"].strip()
            assert question["explanation"].strip()
            assert len(question["options"]) >= 2
            assert sum(1 for _, correct in question["options"] if correct) >= 1


def test_every_lesson_is_substantive():
    seen = set()
    for module in MODULES:
        for lesson in module["lessons"]:
            key = (module["slug"], lesson["slug"])
            assert key not in seen
            seen.add(key)
            assert lesson["title"].strip()
            assert lesson["description"].strip()
            assert lesson["objectives"]
            assert lesson["resources"], f"{key} needs further reading"
            assert len(lesson["content"]) >= 1500, f"{key} is too short"
            assert "##" in lesson["content"], f"{key} needs sections"
            for resource in lesson["resources"]:
                assert resource["title"].strip()
                assert resource["url"].startswith("https://")


def test_exercises_are_well_formed():
    for module, lesson, exercise in EXERCISES:
        where = f"{module['slug']}/{lesson['slug']}/{exercise['title']}"
        assert exercise["description"].strip(), where
        assert exercise["instructions"].strip(), where
        assert exercise["solution"].strip(), where
        assert exercise["starter"].strip(), where
        assert exercise["tests"].strip(), where
        assert exercise["hints"], where
        assert exercise["points"] > 0, where


def test_practice_question_count():
    questions = sum(len(module["quiz"]["questions"]) for module in MODULES)
    assert questions >= 60


def test_projects_are_documented():
    assert PROJECTS, "the curriculum should include portfolio projects"
    for project in PROJECTS:
        assert project["title"].strip()
        assert project["description"].strip()
        assert project["requirements"].strip()
        assert project["rubric"], project["title"]
        assert sum(item["points"] for item in project["rubric"]) == 100
    capstones = [project for project in PROJECTS if project.get("is_capstone")]
    assert len(capstones) == 1


@pytest.mark.parametrize(
    "module,lesson,exercise",
    EXERCISES,
    ids=[f"{m['slug']}::{e['title']}" for m, _, e in EXERCISES],
)
def test_reference_solution_passes_its_tests(module, lesson, exercise):
    source = exercise["solution"] + "\n\n" + exercise["tests"]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "solution_check.py"
        path.write_text(source, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", str(path)],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=directory,
        )
    assert result.returncode == 0, (
        f"{module['slug']}/{lesson['slug']}/{exercise['title']} failed:\n"
        f"{result.stderr[-2000:]}"
    )
