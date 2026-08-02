from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import (
    User, Course, Module, Lesson, Enrollment, Category,
    TechnologyStack, CourseTechnology, ContentStatus, DifficultyLevel,
    UserStats, UserAchievement, Achievement, LessonProgress, Bookmark,
    UserNote, RecentlyViewed, Submission, DailyGoal, Notification,
    Flashcard, Certificate, AIConversation,
)
from app.schemas import (
    UserResponse, UserProfileUpdate, UserPreferences, UserStatsResponse,
    EnrollmentResponse, BookmarkCreate, BookmarkResponse,
    UserNoteCreate, UserNoteResponse, PaginatedResponse,
    NotificationResponse, AchievementResponse,
    FlashcardResponse, DashboardResponse, CourseListItem,
)
from app.utils.deps import get_current_active_user, require_admin
from app.utils.security import hash_password, verify_password
from datetime import datetime, date, timezone
from uuid import UUID

router = APIRouter(prefix="/users", tags=["Users"])


# -- Profile --

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if data.display_name is not None:
        current_user.display_name = data.display_name
    if data.bio is not None:
        current_user.bio = data.bio
    if data.username is not None:
        existing = await db.execute(select(User).where(User.username == data.username, User.id != current_user.id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        current_user.username = data.username

    current_user.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return current_user


@router.put("/me/preferences")
async def update_preferences(
    data: UserPreferences,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.preferences = data.model_dump()
    current_user.updated_at = datetime.now(timezone.utc)
    return {"detail": "Preferences updated", "preferences": current_user.preferences}


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_stats(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = result.scalar_one_or_none()
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        await db.flush()
    return stats


# -- Dashboard --

@router.get("/me/dashboard", response_model=DashboardResponse)
async def get_dashboard(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # Stats
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = stats_result.scalar_one_or_none()
    if not stats:
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        await db.flush()

    # Continue learning - enrollments sorted by last accessed (eager load course)
    enrollments_result = await db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.course))
        .where(Enrollment.user_id == current_user.id, Enrollment.is_completed == False)
        .order_by(Enrollment.last_accessed_at.desc())
        .limit(5)
    )
    enrollments = enrollments_result.scalars().all()

    # Recent activity - submissions, completed lessons
    recent = []

    recent_lessons = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.is_completed == True,
        ).order_by(LessonProgress.completed_at.desc()).limit(10)
    )
    for lp in recent_lessons.scalars().all():
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == lp.lesson_id))
        lesson = lesson_result.scalar_one_or_none()
        if lesson:
            recent.append({
                "type": "lesson_completed",
                "title": lesson.title,
                "lesson_id": str(lp.lesson_id),
                "at": lp.completed_at.isoformat() if lp.completed_at else None,
            })

    # Daily goal
    today = date.today()
    goal_result = await db.execute(
        select(DailyGoal).where(DailyGoal.user_id == current_user.id, DailyGoal.goal_date == today)
    )
    daily_goal = goal_result.scalar_one_or_none()
    goal_dict = None
    if daily_goal:
        goal_dict = {
            "target_minutes": daily_goal.target_minutes,
            "target_lessons": daily_goal.target_lessons,
            "target_exercises": daily_goal.target_exercises,
            "actual_minutes": daily_goal.actual_minutes,
            "actual_lessons": daily_goal.actual_lessons,
            "actual_exercises": daily_goal.actual_exercises,
            "is_completed": daily_goal.is_completed,
        }

    # Achievements
    achievements_result = await db.execute(
        select(Achievement, UserAchievement.unlocked_at)
        .join(UserAchievement, UserAchievement.achievement_id == Achievement.id)
        .where(UserAchievement.user_id == current_user.id)
        .order_by(UserAchievement.unlocked_at.desc())
        .limit(10)
    )
    achievements = []
    for ach, unlocked_at in achievements_result.all():
        ach_dict = AchievementResponse.model_validate(ach).model_dump()
        ach_dict["unlocked_at"] = unlocked_at
        achievements.append(AchievementResponse(**ach_dict))

    # Recommended courses
    recommended_result = await db.execute(
        select(Course)
        .where(Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None))
        .order_by(Course.enrollment_count.desc())
        .limit(6)
    )
    recommended = recommended_result.scalars().all()

    return DashboardResponse(
        user=UserResponse.model_validate(current_user),
        stats=UserStatsResponse.model_validate(stats),
        continue_learning=[EnrollmentResponse.model_validate(e) for e in enrollments],
        recent_activity=recent,
        daily_goal=goal_dict,
        achievements=achievements,
        recommended_courses=[CourseListItem.model_validate(c) for c in recommended],
    )


# -- Enrollments --

@router.get("/me/enrollments", response_model=list[EnrollmentResponse])
async def get_enrollments(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.course))
        .where(Enrollment.user_id == current_user.id)
        .order_by(Enrollment.last_accessed_at.desc())
    )
    return result.scalars().all()


@router.post("/me/enrollments/{course_id}", status_code=status.HTTP_201_CREATED)
async def enroll_course(
    course_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Allow enrollment in any non-deleted course (not just PUBLISHED)
    course_result = await db.execute(
        select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
    )
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id, Enrollment.course_id == course_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already enrolled")

    enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(enrollment)
    course.enrollment_count = (course.enrollment_count or 0) + 1
    return {"detail": "Enrolled successfully"}


# -- Bookmarks --

@router.get("/me/bookmarks", response_model=list[BookmarkResponse])
async def get_bookmarks(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bookmark).where(Bookmark.user_id == current_user.id).order_by(Bookmark.created_at.desc())
    )
    return result.scalars().all()


@router.post("/me/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    data: BookmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    bookmark = Bookmark(
        user_id=current_user.id,
        lesson_id=data.lesson_id,
        exercise_id=data.exercise_id,
        note=data.note,
    )
    db.add(bookmark)
    await db.flush()
    return bookmark


@router.delete("/me/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    await db.delete(bookmark)
    return {"detail": "Bookmark removed"}


# -- Notes --

@router.get("/me/notes", response_model=list[UserNoteResponse])
async def get_notes(
    lesson_id: UUID = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserNote).where(UserNote.user_id == current_user.id)
    if lesson_id:
        query = query.where(UserNote.lesson_id == lesson_id)
    query = query.order_by(UserNote.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/me/notes", response_model=UserNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: UserNoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    note = UserNote(
        user_id=current_user.id,
        lesson_id=data.lesson_id,
        content=data.content,
        is_private=data.is_private,
    )
    db.add(note)
    await db.flush()
    return note


@router.delete("/me/notes/{note_id}")
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserNote).where(UserNote.id == note_id, UserNote.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await db.delete(note)
    return {"detail": "Note deleted"}


# -- Notifications --

@router.get("/me/notifications", response_model=PaginatedResponse)
async def get_notifications(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)

    count_query = select(func.count(Notification.id)).where(Notification.user_id == current_user.id)
    if unread_only:
        count_query = count_query.where(Notification.is_read == False)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    return PaginatedResponse(
        items=[NotificationResponse.model_validate(n) for n in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.post("/me/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    return {"detail": "Marked as read"}


@router.post("/me/notifications/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)
    )
    now = datetime.now(timezone.utc)
    for notif in result.scalars().all():
        notif.is_read = True
        notif.read_at = now
    return {"detail": "All notifications marked as read"}


# -- Admin Users --

@router.get("/", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=""),
    role: str = Query(default=None),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.deleted_at.is_(None))
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%"),
            )
        )
    if role:
        query = query.where(User.role == role)

    count_query = select(func.count(User.id)).where(User.deleted_at.is_(None))
    if search:
        count_query = count_query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.display_name.ilike(f"%{search}%"),
            )
        )
    if role:
        count_query = count_query.where(User.role == role)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(User.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
