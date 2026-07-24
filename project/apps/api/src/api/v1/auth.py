from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.dependencies import get_current_active_user, get_current_user
from src.core.rate_limit import RateLimiter
from src.core.security import (
    create_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_refresh_token,
    validate_password,
    verify_password,
)
from src.db.session import get_db
from src.models.user import RefreshToken, User, UserRole
from src.schemas.auth import ChangePasswordRequest, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenPair
from src.schemas.user import UserRead

router = APIRouter()


async def _create_refresh_token_record(db: AsyncSession, user: User) -> str:
    raw = generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw),
        expires_at=expires_at,
        revoked=False,
    )
    db.add(refresh)
    return raw


async def _revoke_all_refresh_tokens(db: AsyncSession, user_id: UUID) -> None:
    result = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user_id))
    for token in result.scalars().all():
        token.revoked = True


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(RateLimiter("10/minute")),
) -> TokenPair:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if data.password:
        try:
            validate_password(data.password)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    await db.flush()

    db.add(UserRole(user_id=user.id, role="learner"))
    await db.flush()

    access_token = create_access_token({"sub": str(user.id)})
    raw_refresh = await _create_refresh_token_record(db, user)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=raw_refresh)


@router.post("/login", response_model=TokenPair)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(RateLimiter("10/minute")),
) -> TokenPair:
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    raw_refresh = await _create_refresh_token_record(db, user)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=raw_refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(RateLimiter("10/minute")),
) -> TokenPair:
    token_hash = hash_refresh_token(data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
        )
    )
    refresh = result.scalar_one_or_none()
    if refresh is None or refresh.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    # Rotate: revoke old token and issue new pair
    refresh.revoked = True
    access_token = create_access_token({"sub": str(refresh.user_id)})
    user_result = await db.execute(select(User).where(User.id == refresh.user_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    raw_refresh = await _create_refresh_token_record(db, user)
    await db.commit()

    return TokenPair(access_token=access_token, refresh_token=raw_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: LogoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    if data.refresh_token:
        token_hash = hash_refresh_token(data.refresh_token)
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == current_user.id,
            )
        )
        refresh = result.scalar_one_or_none()
        if refresh:
            refresh.revoked = True
    await db.commit()


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    if not current_user.hashed_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No password set")
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    try:
        validate_password(data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await db.delete(current_user)
    await db.commit()

