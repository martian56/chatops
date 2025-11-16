from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid
import secrets
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate
from app.core.security import get_password_hash, verify_password


def generate_api_key() -> str:
    """Generate a secure API key"""
    # Generate a 32-byte random key and encode as hex (64 characters)
    return secrets.token_urlsafe(32)


def hash_api_key(key: str) -> str:
    """Hash an API key for storage"""
    return get_password_hash(key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return verify_password(plain_key, hashed_key)


async def get_api_key(db: AsyncSession, key_id: uuid.UUID) -> Optional[APIKey]:
    """Get API key by ID"""
    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    return result.scalar_one_or_none()


async def get_api_key_by_hash(db: AsyncSession, key_hash: str) -> Optional[APIKey]:
    """Get API key by hash"""
    result = await db.execute(select(APIKey).where(APIKey.key_hash == key_hash))
    return result.scalar_one_or_none()


async def get_api_keys_by_server(
    db: AsyncSession, server_id: uuid.UUID, active_only: bool = False
) -> List[APIKey]:
    """Get all API keys for a server"""
    query = select(APIKey).where(APIKey.server_id == server_id)
    if active_only:
        query = query.where(APIKey.is_active == True)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_api_key(
    db: AsyncSession, key_in: APIKeyCreate, created_by: Optional[uuid.UUID] = None
) -> tuple[APIKey, str]:
    """Create a new API key and return the key object and the plain key"""
    # Generate the API key
    plain_key = generate_api_key()
    key_hash = hash_api_key(plain_key)
    
    db_key = APIKey(
        server_id=key_in.server_id,
        key_hash=key_hash,
        name=key_in.name,
        expires_at=key_in.expires_at,
        created_by=created_by,
    )
    db.add(db_key)
    await db.commit()
    await db.refresh(db_key)
    
    return db_key, plain_key


async def verify_and_get_api_key(db: AsyncSession, plain_key: str) -> Optional[APIKey]:
    """Verify an API key and return the key object if valid"""
    # We need to check all keys - this is not ideal for performance
    # In production, you might want to add an index or use a different approach
    result = await db.execute(select(APIKey).where(APIKey.is_active == True))
    keys = result.scalars().all()
    
    for key in keys:
        if verify_api_key(plain_key, key.key_hash):
            # Update last_used timestamp
            from datetime import datetime
            key.last_used = datetime.utcnow()
            await db.commit()
            await db.refresh(key)
            return key
    
    return None


async def deactivate_api_key(db: AsyncSession, key_id: uuid.UUID) -> bool:
    """Deactivate an API key"""
    db_key = await get_api_key(db, key_id)
    if not db_key:
        return False
    
    db_key.is_active = False
    await db.commit()
    await db.refresh(db_key)
    return True


async def delete_api_key(db: AsyncSession, key_id: uuid.UUID) -> bool:
    """Delete an API key"""
    db_key = await get_api_key(db, key_id)
    if not db_key:
        return False
    
    await db.delete(db_key)
    await db.commit()
    return True


async def get_user_server_ids(db: AsyncSession, user_id: uuid.UUID) -> List[uuid.UUID]:
    """Get all server IDs that belong to a user (through API keys they created)"""
    result = await db.execute(
        select(APIKey.server_id)
        .where(APIKey.created_by == user_id)
        .distinct()
    )
    return [row[0] for row in result.all()]

