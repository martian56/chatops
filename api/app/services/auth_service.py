from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import authenticate_user, create_user, get_user_by_email, get_user_by_username
from app.schemas.user import UserCreate
from app.schemas.auth import Token, RefreshTokenResponse
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings
from app.schemas.user import UserResponse


async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    """Authenticate user and return tokens"""
    user = await authenticate_user(db, email, password)
    if not user:
        raise ValueError("Incorrect email or password")
    
    if not user.is_active:
        raise ValueError("User account is disabled")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=refresh_token_expires,
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


async def register_user(db: AsyncSession, user_in: UserCreate) -> Token:
    """Register a new user and return tokens"""
    # Check if user already exists
    if await get_user_by_email(db, user_in.email):
        raise ValueError("Email already registered")
    
    if await get_user_by_username(db, user_in.username):
        raise ValueError("Username already taken")
    
    # Create user
    user = await create_user(db, user_in)
    
    # Generate tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=refresh_token_expires,
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> RefreshTokenResponse:
    """Refresh an access token using a refresh token"""
    # Decode and verify refresh token
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise ValueError("Invalid refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid refresh token")
    
    # Verify user exists and is active
    from app.crud.user import get_user
    import uuid
    user = await get_user(db, uuid.UUID(user_id))
    if not user:
        raise ValueError("User not found")
    
    if not user.is_active:
        raise ValueError("User account is disabled")
    
    # Generate new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

