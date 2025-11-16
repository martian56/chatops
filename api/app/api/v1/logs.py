from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.log_entry import LogLevel, LogSource
from app.crud import log_entry as crud_log_entry
from app.schemas.log_entry import LogEntryResponse

router = APIRouter()


@router.get("/{server_id}", response_model=List[LogEntryResponse])
async def get_server_logs(
    server_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[LogLevel] = None,
    source: Optional[LogSource] = None,
    component: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get logs for a specific server"""
    # Verify server ownership
    from app.crud import server as crud_server
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    logs = await crud_log_entry.get_log_entries(
        db,
        server_id=server_id,
        level=level,
        source=source,
        component=component,
        limit=limit,
    )
    return logs
