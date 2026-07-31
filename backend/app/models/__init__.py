import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    Column, String, Boolean, Integer, Float, Numeric,
    DateTime, Date, Text, ForeignKey, UniqueConstraint,
    Enum as SAEnum, JSON, CheckConstraint, Index, BigInteger, LargeBinary,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INET
from sqlalchemy.orm import relationship
from app.database import Base

import enum


# ── Enum Types ──────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExerciseType(str, enum.Enum):
    OUTPUT_PREDICTION = "output_prediction"
    DEBUGGING = "debugging"
    CODE_COMPLETION = "code_completion"
    BUG_FIXING = "bug_fixing"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"


class ExerciseDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TRUE_FALSE = "true_false"
    CODING = "coding"
    TEXT = "text"


class FlashcardStatus(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    RELEARNING = "relearning"


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"


class AchievementCategory(str, enum.Enum):
    LEARNING = "learning"
    PRACTICE = "practice"
    STREAK = "streak"
    SOCIAL = "social"
    MILESTONE = "milestone"
    SPECIAL = "special"


class NotificationType(str, enum.Enum):
    SYSTEM = "system"
    COURSE = "course"
    ACHIEVEMENT = "achievement"
    STREAK = "streak"
    REMINDER = "reminder"
    SOCIAL = "social"


# ── Helper Columns ──────────────────────────────────────────────

def uuid_pk():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def timestamps():
    return [
        Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
        Column("updated_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
    ]


def soft_delete():
    return Column("deleted_at", DateTime(timezone=True), nullable=True)


# ── Identity & Access ───────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = uuid_pk()
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    email_verified = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    preferences = Column(JSON, nullable=False, default=dict)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    lesson_progress = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("UserNote", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    user_stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("provider", "provider_user_id"),)

    user = relationship("User", back_populates="oauth_accounts")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    device_info = Column(Text, nullable=True)
    ip_address = Column(INET, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")


# ── Course Structure ────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = uuid_pk()
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    children = relationship("Category", backref="parent", remote_side=[id])


class TechnologyStack(Base):
    __tablename__ = "technology_stacks"

    id = uuid_pk()
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category")


class Course(Base):
    __tablename__ = "courses"

    id = uuid_pk()
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)
    learning_objectives = Column(ARRAY(Text), nullable=True)
    prerequisites = Column(ARRAY(Text), nullable=True)
    difficulty = Column(SAEnum(DifficultyLevel), nullable=False, default=DifficultyLevel.BEGINNER)
    estimated_duration_minutes = Column(Integer, nullable=True)
    status = Column(SAEnum(ContentStatus), nullable=False, default=ContentStatus.DRAFT, index=True)
    image_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    language = Column(String(50), nullable=False, default="english")
    skill_tags = Column(ARRAY(Text), nullable=True)
    module_count = Column(Integer, nullable=False, default=0)
    lesson_count = Column(Integer, nullable=False, default=0)
    enrollment_count = Column(Integer, nullable=False, default=0)
    rating_average = Column(Numeric(3, 2), default=0)
    rating_count = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_free = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.display_order")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    technologies = relationship("CourseTechnology", back_populates="course", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="course")
    projects = relationship("Project", back_populates="course")
    author = relationship("User")


class CourseTechnology(Base):
    __tablename__ = "course_technologies"

    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)
    technology_id = Column(UUID(as_uuid=True), ForeignKey("technology_stacks.id", ondelete="CASCADE"), primary_key=True)

    course = relationship("Course", back_populates="technologies")
    technology = relationship("TechnologyStack")


class Module(Base):
    __tablename__ = "modules"

    id = uuid_pk()
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    learning_objectives = Column(ARRAY(Text), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    lesson_count = Column(Integer, nullable=False, default=0)
    estimated_duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("course_id", "slug"),)

    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.display_order")


class Lesson(Base):
    __tablename__ = "lessons"

    id = uuid_pk()
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    content_markdown = Column(Text, nullable=False)
    learning_objectives = Column(ARRAY(Text), nullable=True)
    difficulty = Column(SAEnum(DifficultyLevel), nullable=False, default=DifficultyLevel.BEGINNER)
    estimated_duration_minutes = Column(Integer, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    skill_tags = Column(ARRAY(Text), nullable=True)
    is_free_preview = Column(Boolean, nullable=False, default=False)
    version = Column(Integer, nullable=False, default=1)
    status = Column(SAEnum(ContentStatus), nullable=False, default=ContentStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("module_id", "slug"),)

    module = relationship("Module", back_populates="lessons")
    resources = relationship("LessonResource", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("LessonProgress", back_populates="lesson")
    exercises = relationship("Exercise", back_populates="lesson")
    quizzes = relationship("Quiz", back_populates="lesson")


class LessonResource(Base):
    __tablename__ = "lesson_resources"

    id = uuid_pk()
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)
    url = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="resources")


# ── Quizzes ─────────────────────────────────────────────────────

class Quiz(Base):
    __tablename__ = "quizzes"

    id = uuid_pk()
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=True, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    passing_score = Column(Integer, nullable=False, default=70)
    time_limit_minutes = Column(Integer, nullable=True)
    question_count = Column(Integer, nullable=False, default=0)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.display_order")


class Question(Base):
    __tablename__ = "questions"

    id = uuid_pk()
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_type = Column(SAEnum(QuestionType), nullable=False, default=QuestionType.MULTIPLE_CHOICE)
    content = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Integer, nullable=False, default=1)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.display_order")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = uuid_pk()
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    display_order = Column(Integer, nullable=False, default=0)

    question = relationship("Question", back_populates="options")


# ── Practice Engine ─────────────────────────────────────────────

class Exercise(Base):
    __tablename__ = "exercises"

    id = uuid_pk()
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    exercise_type = Column(SAEnum(ExerciseType), nullable=False, index=True)
    difficulty = Column(SAEnum(ExerciseDifficulty), nullable=False, default=ExerciseDifficulty.EASY, index=True)
    starter_code = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=False)
    test_code = Column(Text, nullable=True)
    hints = Column(JSON, nullable=False, default=list)
    skill_tags = Column(ARRAY(Text), nullable=True)
    estimated_duration_minutes = Column(Integer, nullable=True)
    points = Column(Integer, nullable=False, default=10)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="exercises")
    course = relationship("Course", back_populates="exercises")
    exercise_hints = relationship("ExerciseHint", back_populates="exercise", cascade="all, delete-orphan", order_by="ExerciseHint.hint_level")


class ExerciseHint(Base):
    __tablename__ = "exercise_hints"

    id = uuid_pk()
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    hint_level = Column(Integer, nullable=False, default=1)
    cost_percentage = Column(Integer, nullable=False, default=0)
    display_order = Column(Integer, nullable=False, default=0)

    exercise = relationship("Exercise", back_populates="exercise_hints")


class Submission(Base):
    __tablename__ = "submissions"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(SAEnum(SubmissionStatus), nullable=False, default=SubmissionStatus.PENDING)
    score = Column(Numeric(5, 2), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_kb = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    test_results = Column(JSON, nullable=True)
    hints_used = Column(Integer, nullable=False, default=0)
    attempt_number = Column(Integer, nullable=False, default=1)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="submissions")
    exercise = relationship("Exercise")


class Project(Base):
    __tablename__ = "projects"

    id = uuid_pk()
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    difficulty = Column(SAEnum(ExerciseDifficulty), nullable=False, default=ExerciseDifficulty.MEDIUM)
    is_capstone = Column(Boolean, nullable=False, default=False)
    estimated_duration_hours = Column(Integer, nullable=True)
    skill_tags = Column(ARRAY(Text), nullable=True)
    starter_files = Column(JSON, nullable=True)
    rubric = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", back_populates="projects")


class ProjectSubmission(Base):
    __tablename__ = "project_submissions"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code_files = Column(JSON, nullable=False)
    review_status = Column(String(50), nullable=False, default="pending")
    review_feedback = Column(Text, nullable=True)
    review_score = Column(Numeric(5, 2), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


# ── Learning Progress ───────────────────────────────────────────

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    progress_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    enrolled_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_accessed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "course_id"),)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, nullable=False, default=False)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    completion_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    last_position = Column(JSON, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)

    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "lesson_id", "exercise_id"),)

    user = relationship("User", back_populates="bookmarks")
    lesson = relationship("Lesson")
    exercise = relationship("Exercise")


class UserNote(Base):
    __tablename__ = "user_notes"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    is_private = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="notes")
    lesson = relationship("Lesson")


class RecentlyViewed(Base):
    __tablename__ = "recently_viewed"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)


# ── Revision System ─────────────────────────────────────────────

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True)
    front_content = Column(Text, nullable=False)
    back_content = Column(Text, nullable=False)
    status = Column(SAEnum(FlashcardStatus), nullable=False, default=FlashcardStatus.NEW)
    ease_factor = Column(Numeric(4, 2), nullable=False, default=2.5)
    interval_days = Column(Integer, nullable=False, default=0)
    repetitions = Column(Integer, nullable=False, default=0)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_flashcards_review", "user_id", "next_review_at", postgresql_where=next_review_at.isnot(None)),
    )

    user = relationship("User", back_populates="flashcards")
    lesson = relationship("Lesson")


class FlashcardReview(Base):
    __tablename__ = "flashcard_reviews"

    id = uuid_pk()
    flashcard_id = Column(UUID(as_uuid=True), ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    quality = Column(Integer, nullable=False)
    time_spent_seconds = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class KnowledgeTopic(Base):
    __tablename__ = "knowledge_topics"

    id = uuid_pk()
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_topics.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    children = relationship("KnowledgeTopic", backref="parent", remote_side=[id])


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = uuid_pk()
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_topics.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_topics.id", ondelete="CASCADE"), nullable=False)
    relationship = Column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint("source_id", "target_id", "relationship"),)


class UserKnowledge(Base):
    __tablename__ = "user_knowledge"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_topics.id", ondelete="CASCADE"), nullable=False)
    mastery_level = Column(Numeric(5, 2), nullable=False, default=0)
    confidence = Column(Numeric(5, 2), nullable=False, default=0)
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)
    assessment_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (UniqueConstraint("user_id", "topic_id"),)


# ── Gamification ────────────────────────────────────────────────

class UserStats(Base):
    __tablename__ = "user_stats"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_xp = Column(Integer, nullable=False, default=0)
    current_level = Column(Integer, nullable=False, default=1)
    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date, nullable=True)
    lessons_completed = Column(Integer, nullable=False, default=0)
    exercises_completed = Column(Integer, nullable=False, default=0)
    projects_completed = Column(Integer, nullable=False, default=0)
    total_time_spent_seconds = Column(BigInteger, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="user_stats")


class Achievement(Base):
    __tablename__ = "achievements"

    id = uuid_pk()
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(100), nullable=False)
    category = Column(SAEnum(AchievementCategory), nullable=False)
    xp_reward = Column(Integer, nullable=False, default=0)
    criteria = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)


class DailyGoal(Base):
    __tablename__ = "daily_goals"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_date = Column(Date, nullable=False)
    target_minutes = Column(Integer, nullable=False, default=30)
    target_lessons = Column(Integer, nullable=False, default=1)
    target_exercises = Column(Integer, nullable=False, default=2)
    actual_minutes = Column(Integer, nullable=False, default=0)
    actual_lessons = Column(Integer, nullable=False, default=0)
    actual_exercises = Column(Integer, nullable=False, default=0)
    is_completed = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("user_id", "goal_date"),)


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    period_type = Column(String(20), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    xp_earned = Column(Integer, nullable=False, default=0)
    rank = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "period_type", "period_start"),)


# ── AI & Chat ───────────────────────────────────────────────────

class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assistant_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=True)
    context_data = Column(JSON, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.created_at")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = uuid_pk()
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    conversation = relationship("AIConversation", back_populates="messages")


# ── Notifications ───────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SAEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


# ── Certificates ────────────────────────────────────────────────

class Certificate(Base):
    __tablename__ = "certificates"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    certificate_number = Column(String(50), unique=True, nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "course_id"),)

    user = relationship("User", back_populates="certificates")
    course = relationship("Course")


# ── Discussion ──────────────────────────────────────────────────

class Discussion(Base):
    __tablename__ = "discussions"

    id = uuid_pk()
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_resolved = Column(Boolean, nullable=False, default=False)
    vote_count = Column(Integer, nullable=False, default=0)
    reply_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiscussionReply(Base):
    __tablename__ = "discussion_replies"

    id = uuid_pk()
    discussion_id = Column(UUID(as_uuid=True), ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("discussion_replies.id"), nullable=True)
    content = Column(Text, nullable=False)
    is_solution = Column(Boolean, nullable=False, default=False)
    vote_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Audit & System ──────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = uuid_pk()
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = uuid_pk()
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=False)
    rules = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
