from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.connection_event import ConnectionEvent, ConnectionEventType


async def create_connection_event(
    db: AsyncSession,
    server_id: uuid.UUID,
    event_type: ConnectionEventType,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    error_message: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    extra_data: Optional[str] = None,
) -> ConnectionEvent:
    """Create a new connection event"""
    event = ConnectionEvent(
        server_id=server_id,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        error_message=error_message,
        duration_seconds=duration_seconds,
        extra_data=extra_data,
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_connection_events(
    db: AsyncSession,
    server_id: Optional[uuid.UUID] = None,
    event_type: Optional[ConnectionEventType] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
) -> List[ConnectionEvent]:
    """Get connection events with filters"""
    query = select(ConnectionEvent)
    
    if server_id:
        query = query.where(ConnectionEvent.server_id == server_id)
    if event_type:
        query = query.where(ConnectionEvent.event_type == event_type)
    if start_time:
        query = query.where(ConnectionEvent.timestamp >= start_time)
    if end_time:
        query = query.where(ConnectionEvent.timestamp <= end_time)
    
    query = query.order_by(desc(ConnectionEvent.timestamp)).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())

