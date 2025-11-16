from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid
from datetime import datetime
from app.models.server import Server, ServerStatus
from app.schemas.server import ServerCreate, ServerUpdate
from app.crud import api_key as crud_api_key


async def get_server(
    db: AsyncSession, 
    server_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
) -> Optional[Server]:
    """Get server by ID - if user_id is provided, verify ownership"""
    result = await db.execute(select(Server).where(Server.id == server_id))
    server = result.scalar_one_or_none()
    
    if server and user_id:
        # Verify that the user owns this server (through API keys)
        user_server_ids = await crud_api_key.get_user_server_ids(db, user_id)
        if server.id not in user_server_ids:
            return None
    
    return server


async def get_servers(
    db: AsyncSession, 
    user_id: Optional[uuid.UUID] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Server]:
    """Get servers - if user_id is provided, only return servers owned by that user"""
    query = select(Server)
    
    if user_id:
        # Get server IDs that belong to this user (through API keys)
        user_server_ids = await crud_api_key.get_user_server_ids(db, user_id)
        if not user_server_ids:
            # User has no servers
            return []
        query = query.where(Server.id.in_(user_server_ids))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_server(db: AsyncSession, server_in: ServerCreate) -> Server:
    """Create a new server"""
    # Use by_alias=False to get actual field names (server_metadata, not metadata)
    data = server_in.model_dump(by_alias=False, exclude_none=True)
    # Ensure server_metadata is explicitly set (None or dict, not missing)
    if "server_metadata" not in data:
        data["server_metadata"] = None
    
    db_server = Server(**data)
    db.add(db_server)
    await db.commit()
    await db.refresh(db_server)
    return db_server


async def update_server(
    db: AsyncSession, server_id: uuid.UUID, server_in: ServerUpdate
) -> Optional[Server]:
    """Update server"""
    db_server = await get_server(db, server_id)
    if not db_server:
        return None
    
    # Use by_alias=False to get actual field names (server_metadata, not metadata)
    update_data = server_in.model_dump(exclude_unset=True, by_alias=False)
    for field, value in update_data.items():
        setattr(db_server, field, value)
    
    await db.commit()
    await db.refresh(db_server)
    return db_server


async def delete_server(db: AsyncSession, server_id: uuid.UUID) -> bool:
    """Delete server (related records are automatically deleted via CASCADE)"""
    db_server = await get_server(db, server_id)
    if not db_server:
        return False
    
    # Delete the server - related records (alerts, thresholds, api_keys, metrics, etc.)
    # will be automatically deleted by database CASCADE constraints
    await db.delete(db_server)
    await db.commit()
    return True


async def update_server_status(
    db: AsyncSession, server_id: uuid.UUID, status: ServerStatus, update_last_seen: bool = False
) -> Optional[Server]:
    """Update server status and optionally last_seen timestamp"""
    db_server = await get_server(db, server_id)
    if not db_server:
        return None
    
    db_server.status = status
    if update_last_seen:
        db_server.last_seen = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_server)
    return db_server

