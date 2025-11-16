from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.log_entry import LogEntry, LogLevel, LogSource


async def create_log_entry(
    db: AsyncSession,
    server_id: Optional[uuid.UUID],
    message: str,
    level: LogLevel = LogLevel.INFO,
    source: LogSource = LogSource.SYSTEM,
    component: Optional[str] = None,
    extra_data: Optional[str] = None,
) -> LogEntry:
    """Create a new log entry"""
    log_entry = LogEntry(
        server_id=server_id,
        level=level,
        source=source,
        message=message,
        component=component,
        extra_data=extra_data,
    )
    
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry


async def get_log_entries(
    db: AsyncSession,
    server_id: Optional[uuid.UUID] = None,
    level: Optional[LogLevel] = None,
    source: Optional[LogSource] = None,
    component: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
) -> List[LogEntry]:
    """Get log entries with filters"""
    query = select(LogEntry)
    
    if server_id:
        query = query.where(LogEntry.server_id == server_id)
    if level:
        query = query.where(LogEntry.level == level)
    if source:
        query = query.where(LogEntry.source == source)
    if component:
        query = query.where(LogEntry.component == component)
    if start_time:
        query = query.where(LogEntry.timestamp >= start_time)
    if end_time:
        query = query.where(LogEntry.timestamp <= end_time)
    
    query = query.order_by(desc(LogEntry.timestamp)).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())

