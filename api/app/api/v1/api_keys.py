from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user, get_api_key_auth
from app.models.user import User
from app.models.api_key import APIKey
from app.crud import api_key as crud_api_key
from app.crud import server as crud_server
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyInfo

router = APIRouter()


@router.get("/me")
async def get_my_api_key_info(
    api_key: APIKey = Depends(get_api_key_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get information about the current API key (for agents)"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    return {
        "server_id": str(api_key.server_id),
        "key_id": str(api_key.id),
        "name": api_key.name,
        "is_active": api_key.is_active,
    }


@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_in: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new API key for a server"""
    # Verify server exists and user owns it
    server = await crud_server.get_server(db, key_in.server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Create the API key
    db_key, plain_key = await crud_api_key.create_api_key(
        db, key_in, created_by=current_user.id
    )
    
    # Return response with the plain key (only shown once)
    return APIKeyResponse(
        id=db_key.id,
        server_id=db_key.server_id,
        key=plain_key,  # Only returned on creation
        name=db_key.name,
        is_active=db_key.is_active,
        last_used=db_key.last_used,
        expires_at=db_key.expires_at,
        created_at=db_key.created_at,
    )


@router.get("/server/{server_id}", response_model=List[APIKeyInfo])
async def get_server_api_keys(
    server_id: uuid.UUID,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all API keys for a server"""
    # Verify server exists and user owns it
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    keys = await crud_api_key.get_api_keys_by_server(db, server_id, active_only=active_only)
    return [APIKeyInfo.model_validate(k) for k in keys]


@router.post("/{key_id}/deactivate", response_model=APIKeyInfo)
async def deactivate_api_key(
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate an API key (only if belongs to user's server)"""
    # Verify ownership first
    key = await crud_api_key.get_api_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Verify the API key belongs to a server owned by the user
    server = await crud_server.get_server(db, key.server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="API key not found")
    
    success = await crud_api_key.deactivate_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key = await crud_api_key.get_api_key(db, key_id)
    return APIKeyInfo.model_validate(key)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an API key (only if belongs to user's server)"""
    # Verify ownership first
    key = await crud_api_key.get_api_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Verify the API key belongs to a server owned by the user
    server = await crud_server.get_server(db, key.server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="API key not found")
    
    success = await crud_api_key.delete_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return None
