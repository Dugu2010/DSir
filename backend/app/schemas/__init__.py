from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum


# ── Common ──────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort: Optional[str] = None
    order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    errors: Optional[list[dict]] = None


# ── Auth ────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ── Users ───────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    display_name: str
    avatar_url: Optional[str]
    bio: Optional[str]
    role: str
    email_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=500)
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)


class UserPreferences(BaseModel):
    theme: Optional[str] = Field(default="system", pattern="^(light|dark|system)$")
    font_size: Optional[str] = Field(default="medium", pattern="^(small|medium|large)$")
    email_notifications: Optional[bool] = True
    push_notifications: Optional[bool] = True
    daily_goal_minutes: Optional[int] = Field(default=30, ge=5, le=480)
    language: Optional[str] = "en"


class UserStatsResponse(BaseModel):
    total_xp: int
    current_level: int
    current_streak: int
    longest_streak: int
    lessons_completed: int
    exercises_completed: int
    projects_completed: int
    total_time_spent_seconds: int

    class Config:
        from_attributes = True


# ── Courses ─────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: str
    long_description: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    prerequisites: Optional[list[str]] = None
    difficulty: str = "beginner"
    estimated_duration_minutes: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    language: str = "english"
    skill_tags: Optional[list[str]] = None
    is_free: bool = True
    category_ids: Optional[list[UUID]] = None
    technology_ids: Optional[list[UUID]] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    prerequisites: Optional[list[str]] = None
    difficulty: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    skill_tags: Optional[list[str]] = None
    is_free: Optional[bool] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None


class CourseResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    description: str
    long_description: Optional[str]
    learning_objectives: Optional[list[str]]
    prerequisites: Optional[list[str]]
    difficulty: str
    estimated_duration_minutes: Optional[int]
    status: str
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    language: str
    skill_tags: Optional[list[str]]
    module_count: int
    lesson_count: int
    enrollment_count: int
    rating_average: float
    rating_count: int
    is_featured: bool
    is_free: bool
    author_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


class CourseListItem(BaseModel):
    id: UUID
    title: str
    slug: str
    description: str
    difficulty: str
    estimated_duration_minutes: Optional[int]
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    skill_tags: Optional[list[str]]
    module_count: int
    lesson_count: int
    enrollment_count: int
    rating_average: float
    is_featured: bool
    is_free: bool
    published_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Modules ─────────────────────────────────────────────────────

class ModuleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    display_order: int = 0
    estimated_duration_minutes: Optional[int] = None


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    display_order: Optional[int] = None
    estimated_duration_minutes: Optional[int] = None


class ModuleResponse(BaseModel):
    id: UUID
    course_id: UUID
    title: str
    slug: str
    description: Optional[str]
    learning_objectives: Optional[list[str]]
    display_order: int
    lesson_count: int
    estimated_duration_minutes: Optional[int]

    class Config:
        from_attributes = True


# ── Lessons ─────────────────────────────────────────────────────

class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    content: str
    content_markdown: str
    learning_objectives: Optional[list[str]] = None
    difficulty: str = "beginner"
    estimated_duration_minutes: Optional[int] = None
    display_order: int = 0
    skill_tags: Optional[list[str]] = None
    is_free_preview: bool = False


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    content_markdown: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    difficulty: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    display_order: Optional[int] = None
    skill_tags: Optional[list[str]] = None
    is_free_preview: Optional[bool] = None
    status: Optional[str] = None


class LessonResponse(BaseModel):
    id: UUID
    module_id: UUID
    title: str
    slug: str
    description: Optional[str]
    content: str
    content_markdown: str
    learning_objectives: Optional[list[str]]
    difficulty: str
    estimated_duration_minutes: Optional[int]
    display_order: int
    skill_tags: Optional[list[str]]
    is_free_preview: bool
    version: int
    status: str
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class LessonListItem(BaseModel):
    id: UUID
    module_id: UUID
    title: str
    slug: str
    description: Optional[str]
    difficulty: str
    estimated_duration_minutes: Optional[int]
    display_order: int
    is_free_preview: bool
    status: str

    class Config:
        from_attributes = True


# ── Quizzes ─────────────────────────────────────────────────────

class QuizResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    passing_score: int
    time_limit_minutes: Optional[int]
    question_count: int

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: UUID
    question_type: str
    content: str
    explanation: Optional[str]
    points: int
    options: list["QuestionOptionResponse"]

    class Config:
        from_attributes = True


class QuestionOptionResponse(BaseModel):
    id: UUID
    content: str
    is_correct: bool

    class Config:
        from_attributes = True


class QuizSubmission(BaseModel):
    answers: dict[str, Any]


# ── Exercises ───────────────────────────────────────────────────

class ExerciseResponse(BaseModel):
    id: UUID
    lesson_id: Optional[UUID]
    title: str
    description: str
    instructions: str
    exercise_type: str
    difficulty: str
    starter_code: Optional[str]
    skill_tags: Optional[list[str]]
    estimated_duration_minutes: Optional[int]
    points: int
    hints_count: int = 0

    class Config:
        from_attributes = True


class ExerciseDetailResponse(ExerciseResponse):
    hints: list[dict]
    test_count: int


class CodeSubmission(BaseModel):
    code: str
    language: str


class SubmissionResponse(BaseModel):
    id: UUID
    exercise_id: UUID
    status: str
    score: Optional[float]
    execution_time_ms: Optional[int]
    memory_used_kb: Optional[int]
    error_message: Optional[str]
    test_results: Optional[dict]
    hints_used: int
    attempt_number: int
    submitted_at: datetime

    class Config:
        from_attributes = True


# ── Learning Progress ──────────────────────────────────────────

class EnrollmentResponse(BaseModel):
    id: UUID
    course: CourseResponse
    progress_percentage: float
    is_completed: bool
    completed_at: Optional[datetime]
    enrolled_at: datetime
    last_accessed_at: datetime

    class Config:
        from_attributes = True


class LessonProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    time_spent_seconds: Optional[int] = None
    completion_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    last_position: Optional[dict] = None


class BookmarkCreate(BaseModel):
    lesson_id: Optional[UUID] = None
    exercise_id: Optional[UUID] = None
    note: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: UUID
    lesson_id: Optional[UUID]
    exercise_id: Optional[UUID]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserNoteCreate(BaseModel):
    lesson_id: UUID
    content: str
    is_private: bool = True


class UserNoteResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    content: str
    is_private: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Flashcards ──────────────────────────────────────────────────

class FlashcardCreate(BaseModel):
    lesson_id: Optional[UUID] = None
    front_content: str
    back_content: str


class FlashcardResponse(BaseModel):
    id: UUID
    lesson_id: Optional[UUID]
    front_content: str
    back_content: str
    status: str
    ease_factor: float
    interval_days: int
    repetitions: int
    last_reviewed_at: Optional[datetime]
    next_review_at: Optional[datetime]

    class Config:
        from_attributes = True


class FlashcardReviewSubmit(BaseModel):
    quality: int = Field(ge=0, le=5)
    time_spent_seconds: Optional[int] = None


# ── Achievements ────────────────────────────────────────────────

class AchievementResponse(BaseModel):
    id: UUID
    name: str
    description: str
    icon: str
    category: str
    xp_reward: int
    unlocked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Dashboard ───────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    user: UserResponse
    stats: UserStatsResponse
    continue_learning: list[EnrollmentResponse]
    recent_activity: list[dict]
    daily_goal: Optional[dict]
    achievements: list[AchievementResponse]
    recommended_courses: list[CourseListItem]


# ── AI ──────────────────────────────────────────────────────────

class AIConversationCreate(BaseModel):
    assistant_type: str = "tutor"
    title: Optional[str] = None
    context_data: Optional[dict] = None


class AIMessageCreate(BaseModel):
    content: str


class AIConversationResponse(BaseModel):
    id: UUID
    assistant_type: str
    title: Optional[str]
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True


class AIMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    tokens_used: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notifications ───────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    body: Optional[str]
    data: Optional[dict]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Admin ───────────────────────────────────────────────────────

class FeatureFlag(BaseModel):
    name: str
    description: Optional[str] = None
    is_enabled: bool = False
    rules: Optional[dict] = None

    class Config:
        from_attributes = True


class AdminDashboardStats(BaseModel):
    total_users: int
    total_courses: int
    total_enrollments: int
    total_completions: int
    active_today: int
    new_users_week: int


# ── Search ──────────────────────────────────────────────────────

class SearchResult(BaseModel):
    courses: list[CourseListItem] = []
    lessons: list[LessonListItem] = []


# ── Rebuild forward refs ────────────────────────────────────────

QuestionResponse.model_rebuild()
