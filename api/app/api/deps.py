from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.crud.user import get_user
from app.crud.api_key import verify_and_get_api_key
from app.core.security import decode_access_token
from app.models.user import User
from app.models.api_key import APIKey
import uuid
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = await get_user(db, uuid.UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user


async def get_api_key_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Optional[APIKey]:
    """Get API key from header if present"""
    if not x_api_key:
        return None
    
    api_key = await verify_and_get_api_key(db, x_api_key)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive",
        )
    
    return api_key


async def get_current_user_or_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    api_key: Optional[APIKey] = Depends(get_api_key_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get current user (JWT) or API key - allows both authentication methods"""
    if api_key:
        # Return API key info for agent authentication
        return {"type": "api_key", "api_key": api_key, "server_id": api_key.server_id}
    
    if credentials:
        # Try JWT auth
        token = credentials.credentials
        try:
            user = await get_current_user(token, db)
            return {"type": "user", "user": user}
        except HTTPException:
            pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
