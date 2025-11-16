from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services.auth_service import login_user, register_user, refresh_access_token
from app.schemas.auth import Token, RefreshTokenRequest, RefreshTokenResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate, PasswordChange
from app.api.deps import get_current_user
from app.models.user import User
from app.crud import user as crud_user

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    username: str = Form(),
    password: str = Form(),
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint (OAuth2 compatible)"""
    try:
        # OAuth2 uses 'username' but we expect email
        token = await login_user(db, username, password)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    try:
        token = await register_user(db, user_in)
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    token_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh an access token using a refresh token"""
    try:
        response = await refresh_access_token(db, token_in.refresh_token)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (client should discard tokens)"""
    return {"message": "Logged out successfully"}


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile"""
    # Only allow updating full_name for now (email/username changes require more validation)
    update_data = UserUpdate(full_name=user_update.full_name)
    updated_user = await crud_user.update_user(db, current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(updated_user)


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password"""
    success = await crud_user.change_password(
        db,
        current_user.id,
        password_change.current_password,
        password_change.new_password,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    return {"message": "Password changed successfully"}

