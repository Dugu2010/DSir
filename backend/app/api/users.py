from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, case
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models import User, Course, Module, Lesson, Exercise, UserStats, ContentStatus, DifficultyLevel, Enrollment, Bookmark, UserNote, Notification
from app.models import LessonProgress
from app.models import User as UserModel
from app.schemas import (
    UserResponse, UserProfileUpdate, UserStatsResponse, DashboardResponse,
    EnrollmentResponse, BookmarkResponse, UserNoteCreate, UserNoteResponse,
    PaginatedResponse,
)
from app.utils.deps import get_current_active_user, get_current_user
from app.utils.auth import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


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
    if data.username is not None:
        existing = await db.execute(select(User).where(User.username == data.username, User.id != current_user.id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")
        current_user.username = data.username
    current_user.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.commit()
    return current_user


@router.put("/me/preferences")
async def update_preferences(
    preferences: dict = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.preferences = preferences
    await db.flush()
    await db.commit()
    return {"detail": "Preferences updated"}


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_stats(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = stats_result.scalar_one_or_none()
    return stats or UserStats(user_id=current_user.id)


@router.get("/me/dashboard", response_model=DashboardResponse)
async def get_dashboard(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = stats_result.scalar_one_or_none()
    enrollments_result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id).order_by(Enrollment.last_accessed_at.desc().nulls_last()).limit(5)
    )
    enrollments = enrollments_result.scalars().all()
    all_enrollments_result = await db.execute(select(Enrollment).where(Enrollment.user_id == current_user.id))
    all_enrollments = all_enrollments_result.scalars().all()
    total_enrolled = len(all_enrollments)
    total_completed = sum(1 for e in all_enrollments if e.is_completed)
    lessons_completed_result = await db.execute(
        select(func.count(LessonProgress.id)).where(LessonProgress.user_id == current_user.id, LessonProgress.is_completed == True)
    )
    lessons_completed = lessons_completed_result.scalar() or 0
    enrolled_course_ids = [e.course_id for e in all_enrollments]
    total_lessons = 0
    if enrolled_course_ids:
        total_lessons_result = await db.execute(
            select(func.count(Lesson.id)).select_from(Lesson).join(Module).where(Module.course_id.in_(enrolled_course_ids))
        )
        total_lessons = total_lessons_result.scalar() or 0
    streak = 0
    today = datetime.now(timezone.utc).date()
    for i in range(365):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(day, datetime.max.time(), tzinfo=timezone.utc)
        has = await db.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == current_user.id,
                LessonProgress.completed_at >= day_start,
                LessonProgress.completed_at <= day_end,
            ).limit(1)
        )
        if has.scalar_one_or_none():
            streak += 1
        elif i > 0:
            break
    popular_result = await db.execute(
        select(Course).where(Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None)).order_by(Course.enrollment_count.desc()).limit(4)
    )
    from app.schemas import CourseResponse
    popular_courses = [CourseResponse.model_validate(c) for c in popular_result.scalars().all()]
    return DashboardResponse(
        total_xp=stats.total_xp if stats else 0, lessons_completed=lessons_completed,
        courses_enrolled=total_enrolled, courses_completed=total_completed,
        total_lessons=total_lessons, streak_days=streak,
        continue_learning=[EnrollmentResponse.model_validate(e) for e in enrollments],
        popular_courses=popular_courses,
    )


@router.get("/me/enrollments", response_model=list[EnrollmentResponse])
async def get_enrollments(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id).order_by(Enrollment.enrolled_at.desc())
    )
    return result.scalars().all()


@router.post("/me/enrollments/{course_id}", status_code=status.HTTP_201_CREATED)
async def enroll_course(
    course_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
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


@router.get("/me/bookmarks", response_model=list[BookmarkResponse])
async def get_bookmarks(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bookmark).where(Bookmark.user_id == current_user.id).order_by(Bookmark.created_at.desc())
    )
    return result.scalars().all()


@router.post("/me/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    course_id: UUID = Body(..., embed=True),
    lesson_id: UUID = Body(None, embed=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    bookmark = Bookmark(user_id=current_user.id, course_id=course_id, lesson_id=lesson_id)
    db.add(bookmark)
    return bookmark


@router.delete("/me/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id))
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    await db.delete(bookmark)
    return {"detail": "Bookmark deleted"}


@router.get("/me/notes", response_model=list[UserNoteResponse])
async def get_notes(
    lesson_id: UUID = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserNote).where(UserNote.user_id == current_user.id)
    if lesson_id:
        query = query.where(UserNote.lesson_id == lesson_id)
    result = await db.execute(query.order_by(UserNote.updated_at.desc()))
    return result.scalars().all()


@router.post("/me/notes", response_model=UserNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: UserNoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    note = UserNote(
        user_id=current_user.id, lesson_id=data.lesson_id,
        content=data.content, note_type=data.note_type or "general",
    )
    db.add(note)
    return note


@router.delete("/me/notes/{note_id}")
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserNote).where(UserNote.id == note_id, UserNote.user_id == current_user.id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await db.delete(note)
    return {"detail": "Note deleted"}


@router.get("/me/notifications", response_model=PaginatedResponse)
async def get_notifications(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    count_result = await db.execute(select(func.count(Notification.id)).where(Notification.user_id == current_user.id))
    total = count_result.scalar() or 0
    result = await db.execute(query.order_by(Notification.created_at.desc()).offset((page - 1) * size).limit(size))
    notifications = result.scalars().all()
    return PaginatedResponse(
        items=[{"id": str(n.id), "type": n.type, "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else None} for n in notifications],
        total=total, page=page, size=size, pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.post("/me/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id))
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification.is_read = True
    return {"detail": "Marked as read"}


@router.post("/me/notifications/read-all")
async def mark_all_read(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False))
    for n in result.scalars().all():
        n.is_read = True
    return {"detail": "All marked as read"}
