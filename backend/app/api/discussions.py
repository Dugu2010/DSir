from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Discussion, DiscussionReply, Notification, NotificationType
from app.schemas import (
    DiscussionCreate, DiscussionResponse,
    DiscussionReplyCreate, DiscussionReplyResponse,
    VoteRequest, PaginatedResponse,
)
from app.utils.deps import get_current_active_user
from app.models import User
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(prefix="/discussions", tags=["Discussions"])


# ── List Discussions ────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse)
async def list_discussions(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    lesson_id: UUID = Query(default=None),
    course_id: UUID = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Discussion)
    if lesson_id:
        query = query.where(Discussion.lesson_id == lesson_id)
    if course_id:
        from app.models import Lesson, Module
        query = query.join(Lesson).join(Module).where(Module.course_id == course_id)

    count_query = select(func.count(Discussion.id)).select_from(Discussion)
    if lesson_id:
        count_query = count_query.where(Discussion.lesson_id == lesson_id)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Discussion.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    discussions = result.scalars().all()

    # Resolve author display names in one query.
    names = {}
    if discussions:
        name_rows = await db.execute(
            select(User.id, User.display_name).where(User.id.in_([d.user_id for d in discussions]))
        )
        names = {str(uid): dn for uid, dn in name_rows.all()}

    items = []
    for d in discussions:
        resp = DiscussionResponse.model_validate(d)
        resp.display_name = names.get(str(d.user_id), "")
        resp.replies = []
        items.append(resp.model_dump())

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


# ── Create Discussion ───────────────────────────────────────────

@router.post("/", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    data: DiscussionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    discussion = Discussion(
        lesson_id=data.lesson_id,
        user_id=current_user.id,
        title=data.title,
        content=data.content,
    )
    db.add(discussion)
    await db.flush()
    await db.commit()

    resp = DiscussionResponse.model_validate(discussion)
    resp.display_name = current_user.display_name
    resp.replies = []
    return resp


# ── Get Discussion with Replies ─────────────────────────────────

@router.get("/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = result.scalar_one_or_none()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")

    replies_result = await db.execute(
        select(DiscussionReply)
        .where(DiscussionReply.discussion_id == discussion_id)
        .order_by(DiscussionReply.created_at)
    )
    reply_rows = replies_result.scalars().all()

    reply_names = {}
    if reply_rows:
        name_rows = await db.execute(
            select(User.id, User.display_name).where(User.id.in_([r.user_id for r in reply_rows]))
        )
        reply_names = {str(uid): dn for uid, dn in name_rows.all()}

    replies = []
    for r in reply_rows:
        rr = DiscussionReplyResponse.model_validate(r)
        rr.display_name = reply_names.get(str(r.user_id), "")
        replies.append(rr)

    author = (await db.execute(
        select(User).where(User.id == discussion.user_id)
    )).scalar_one_or_none()

    resp = DiscussionResponse.model_validate(discussion)
    resp.display_name = author.display_name if author else ""
    resp.replies = replies
    return resp


# ── Add Reply ───────────────────────────────────────────────────

@router.post("/{discussion_id}/replies", response_model=DiscussionReplyResponse, status_code=status.HTTP_201_CREATED)
async def add_reply(
    discussion_id: UUID,
    data: DiscussionReplyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    disc_result = await db.execute(select(Discussion).where(Discussion.id == discussion_id))
    discussion = disc_result.scalar_one_or_none()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")

    reply = DiscussionReply(
        discussion_id=discussion_id,
        user_id=current_user.id,
        parent_id=data.parent_id,
        content=data.content,
    )
    db.add(reply)

    # Update reply count
    discussion.reply_count += 1
    discussion.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.commit()

    resp = DiscussionReplyResponse.model_validate(reply)
    resp.display_name = current_user.display_name
    return resp


# ── Mark as Solution ────────────────────────────────────────────

@router.put("/replies/{reply_id}/solution")
async def mark_solution(
    reply_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    reply_result = await db.execute(select(DiscussionReply).where(DiscussionReply.id == reply_id))
    reply = reply_result.scalar_one_or_none()
    if not reply:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found")

    disc_result = await db.execute(select(Discussion).where(Discussion.id == reply.discussion_id))
    discussion = disc_result.scalar_one_or_none()

    # Only discussion author or admin can mark solutions
    if discussion and discussion.user_id != current_user.id and current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    reply.is_solution = True
    if discussion:
        discussion.is_resolved = True
        discussion.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.commit()

    return {"detail": "Marked as solution"}


# ── Vote on Reply ───────────────────────────────────────────────

@router.post("/replies/{reply_id}/vote")
async def vote_reply(
    reply_id: UUID,
    data: VoteRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    reply_result = await db.execute(select(DiscussionReply).where(DiscussionReply.id == reply_id))
    reply = reply_result.scalar_one_or_none()
    if not reply:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found")

    if reply.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot vote on your own reply")

    if data.direction == "up":
        reply.vote_count += 1
    elif data.direction == "down":
        reply.vote_count -= 1

    await db.flush()
    await db.commit()

    return {"vote_count": reply.vote_count}
