from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, RefreshToken, UserStats
from app.schemas import (
    UserCreate, UserLogin, TokenResponse,
    RefreshTokenRequest, PasswordChangeRequest, UserResponse,
    PasswordResetRequest, PasswordResetConfirm,
)
from app.utils.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, generate_password_reset_token,
)
from app.utils.deps import get_current_active_user
from app.services.email import send_email
from datetime import datetime, timezone
from uuid import UUID
import asyncio
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Redis token helpers (password reset + email verification) ──

async def _redis_set(key: str, value: str, ttl: int) -> None:
    from app.utils.redis import get_redis_client
    client = await get_redis_client()
    await client.set(key, value, ex=ttl)


async def _redis_get(key: str):
    from app.utils.redis import get_redis_client
    client = await get_redis_client()
    val = await client.get(key)
    return val.decode() if val else None


async def _redis_delete(key: str) -> None:
    from app.utils.redis import get_redis_client
    client = await get_redis_client()
    await client.delete(key)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate, db: AsyncSession = Depends(get_db)):
    if not settings.ENABLE_REGISTRATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registration is currently disabled")

    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    existing_user = await db.execute(select(User).where(User.username == data.username))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        display_name=data.display_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()

    stats = UserStats(user_id=user.id)
    db.add(stats)
    await db.flush()

    access_token = create_access_token(str(user.id), user.role.value)
    raw_refresh, token_hash, expires_at = create_refresh_token(str(user.id), user.role.value)

    refresh = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh)

    # Queue an email verification link (no-op if SMTP is not configured).
    asyncio.create_task(_send_verification(user))

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    user.last_login_at = datetime.now(timezone.utc)
    user.last_active_at = datetime.now(timezone.utc)

    access_token = create_access_token(str(user.id), user.role.value)
    raw_refresh, token_hash, expires_at = create_refresh_token(str(user.id), user.role.value)

    refresh = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        ip_address=request.client.host if request.client else None,
    )
    db.add(refresh)

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    import hashlib
    token_hash = hashlib.sha256(data.refresh_token.encode()).hexdigest()

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    token.revoked_at = datetime.now(timezone.utc)

    user_result = await db.execute(select(User).where(User.id == token.user_id, User.deleted_at.is_(None)))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    access_token = create_access_token(str(user.id), user.role.value)
    raw_refresh, new_hash, expires_at = create_refresh_token(str(user.id), user.role.value)

    new_token = RefreshToken(
        user_id=user.id,
        token_hash=new_hash,
        expires_at=expires_at,
    )
    db.add(new_token)

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    tokens = result.scalars().all()
    now = datetime.now(timezone.utc)
    for token in tokens:
        token.revoked_at = now

    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/change-password")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.password_hash = hash_password(data.new_password)
    return {"detail": "Password changed successfully"}


# ── Password Reset ──────────────────────────────────────────────

async def _send_verification(user: User) -> None:
    token = generate_password_reset_token()
    try:
        await _redis_set(f"verify:{token}", str(user.id), ttl=86400)
    except Exception:
        return
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    await asyncio.to_thread(
        send_email,
        user.email,
        "Verify your DSir email",
        f'<p>Welcome to DSir! Verify your email to unlock your account:</p>'
        f'<p><a href="{link}">{link}</a></p>',
    )


@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    generic = {"detail": "If that email is registered, a reset link has been sent."}
    result = await db.execute(
        select(User).where(User.email == data.email, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        return generic

    token = generate_password_reset_token()
    try:
        await _redis_set(f"pwreset:{token}", str(user.id), ttl=1800)
    except Exception:
        raise HTTPException(status_code=503, detail="Reset service unavailable. Try again later.")

    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    await asyncio.to_thread(
        send_email,
        user.email,
        "Reset your DSir password",
        f'<p>Click below to reset your DSir password:</p>'
        f'<p><a href="{link}">{link}</a></p>'
        f'<p>This link expires in 30 minutes.</p>',
    )

    if settings.EMAIL_TOKEN_IN_RESPONSE or settings.DEBUG:
        return {**generic, "reset_token": token, "reset_link": link}
    return generic


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    try:
        user_id = await _redis_get(f"pwreset:{data.token}")
    except Exception:
        raise HTTPException(status_code=503, detail="Reset service unavailable. Try again later.")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.id == UUID(user_id), User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user.password_hash = hash_password(data.new_password)
    await _redis_delete(f"pwreset:{data.token}")

    # Revoke all refresh tokens so stolen sessions can't survive a reset.
    tokens = await db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
    )
    now = datetime.now(timezone.utc)
    for t in tokens.scalars().all():
        t.revoked_at = now

    return {"detail": "Password reset successfully. You can now sign in."}


# ── Email Verification ──────────────────────────────────────────

@router.post("/verify-email")
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    try:
        user_id = await _redis_get(f"verify:{token}")
    except Exception:
        raise HTTPException(status_code=503, detail="Verification service unavailable. Try again later.")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user.email_verified = True
    await _redis_delete(f"verify:{token}")
    return {"detail": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(current_user: User = Depends(get_current_active_user)):
    if current_user.email_verified:
        return {"detail": "Email already verified"}
    await _send_verification(current_user)
    return {"detail": "Verification email sent"}
