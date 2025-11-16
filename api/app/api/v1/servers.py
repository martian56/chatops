from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.audit_log import AuditAction
from app.crud import server as crud_server
from app.schemas.server import Server, ServerCreate, ServerUpdate, ServerResponse
from app.services.audit_service import log_audit

router = APIRouter()


@router.get("", response_model=List[ServerResponse])
async def get_servers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all servers"""
    servers = await crud_server.get_servers(db, skip=skip, limit=limit)
    return [
        ServerResponse(
            id=s.id,
            name=s.name,
            host=s.host,
            port=s.port,
            server_metadata=s.server_metadata,
            status=s.status,
            health_status=s.health_status,
            last_seen=s.last_seen,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in servers
    ]


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get server by ID"""
    server = await crud_server.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return ServerResponse(
        id=server.id,
        name=server.name,
        host=server.host,
        port=server.port,
        server_metadata=server.server_metadata,
        status=server.status,
        health_status=server.health_status,
        last_seen=server.last_seen,
        created_at=server.created_at,
        updated_at=server.updated_at,
    )


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_in: ServerCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new server"""
    server = await crud_server.create_server(db, server_in)
    
    # Log audit event
    await log_audit(
        db,
        action=AuditAction.SERVER_CREATED,
        description=f"Created server: {server.name}",
        user_id=current_user.id,
        server_id=server.id,
        metadata={"server_name": server.name, "host": server.host, "port": server.port},
        request=request,
    )
    
    # Manually construct response to avoid metadata conflict
    return ServerResponse(
        id=server.id,
        name=server.name,
        host=server.host,
        port=server.port,
        server_metadata=server.server_metadata,
        status=server.status,
        health_status=server.health_status,
        last_seen=server.last_seen,
        created_at=server.created_at,
        updated_at=server.updated_at,
    )


@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: uuid.UUID,
    server_in: ServerUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update server"""
    server = await crud_server.update_server(db, server_id, server_in)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Log audit event
    await log_audit(
        db,
        action=AuditAction.SERVER_UPDATED,
        description=f"Updated server: {server.name}",
        user_id=current_user.id,
        server_id=server.id,
        metadata={"changes": server_in.dict(exclude_unset=True)},
        request=request,
    )
    
    return ServerResponse(
        id=server.id,
        name=server.name,
        host=server.host,
        port=server.port,
        server_metadata=server.server_metadata,
        status=server.status,
        health_status=server.health_status,
        last_seen=server.last_seen,
        created_at=server.created_at,
        updated_at=server.updated_at,
    )


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete server"""
    # Get server info before deletion for audit log
    server = await crud_server.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    server_name = server.name
    success = await crud_server.delete_server(db, server_id)
    
    # Log audit event
    await log_audit(
        db,
        action=AuditAction.SERVER_DELETED,
        description=f"Deleted server: {server_name}",
        user_id=current_user.id,
        server_id=server_id,
        metadata={"server_name": server_name},
        request=request,
    )
    
    return None


@router.post("/{server_id}/health")
async def check_server_health(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check server health (placeholder - will be implemented by agent)"""
    server = await crud_server.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # TODO: Implement actual health check via agent
    return {"status": "unknown", "message": "Health check not yet implemented"}

