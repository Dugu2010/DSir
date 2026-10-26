from app.services.gamification import _meets_criteria


def test_legacy_achievement_rules_remain_supported():
    context = {
        "lessons_completed": 1,
        "exercises_completed": 10,
        "current_streak": 7,
        "courses_completed": 1,
        "perfect_score": True,
        "html_completed": False,
        "js_completed": False,
    }

    assert _meets_criteria({"type": "python-starter"}, context)
    assert _meets_criteria({"type": "code-warrior"}, context)
    assert _meets_criteria({"type": "week-streak"}, context)
    assert _meets_criteria({"type": "perfect-score"}, context)
    assert not _meets_criteria({"type": "html-master"}, context)


def test_threshold_achievement_rules_use_real_progress():
    context = {
        "lessons_completed": 12,
        "exercises_completed": 4,
        "current_streak": 3,
        "courses_completed": 0,
        "discussions_created": 1,
        "replies_created": 5,
        "quizzes_passed": 1,
        "total_xp": 1000,
    }

    assert _meets_criteria({"type": "lessons-completed", "threshold": 10}, context)
    assert not _meets_criteria({"type": "lessons-completed", "threshold": 20}, context)
    assert _meets_criteria({"type": "discussions-created", "threshold": 1}, context)
    assert _meets_criteria({"type": "replies-created", "threshold": 5}, context)
    assert _meets_criteria({"type": "quizzes-passed", "threshold": 1}, context)
    assert _meets_criteria({"type": "total-xp", "threshold": 1000}, context)
