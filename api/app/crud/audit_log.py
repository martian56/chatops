from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from app.models.audit_log import AuditLog, AuditAction


async def create_audit_log(
    db: AsyncSession,
    action: AuditAction,
    description: str,
    user_id: Optional[uuid.UUID] = None,
    server_id: Optional[uuid.UUID] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """Create a new audit log entry"""
    audit_log = AuditLog(
        user_id=user_id,
        server_id=server_id,
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message,
        extra_data=metadata,
    )
    
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    return audit_log


async def get_audit_logs(
    db: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    server_id: Optional[uuid.UUID] = None,
    action: Optional[AuditAction] = None,
    success: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
) -> List[AuditLog]:
    """Get audit logs with filters"""
    query = select(AuditLog)
    
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if server_id:
        query = query.where(AuditLog.server_id == server_id)
    if action:
        query = query.where(AuditLog.action == action)
    if success is not None:
        query = query.where(AuditLog.success == success)
    if start_time:
        query = query.where(AuditLog.timestamp >= start_time)
    if end_time:
        query = query.where(AuditLog.timestamp <= end_time)
    
    query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())

