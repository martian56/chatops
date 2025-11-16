"""Audit logging service for tracking user actions"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import uuid
from app.models.audit_log import AuditAction
from app.crud import audit_log as crud_audit_log
from fastapi import Request


async def log_audit(
    db: AsyncSession,
    action: AuditAction,
    description: str,
    user_id: Optional[uuid.UUID] = None,
    server_id: Optional[uuid.UUID] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
):
    """
    Log an audit event
    
    Args:
        db: Database session
        action: The action that was performed
        description: Human-readable description of the action
        user_id: ID of the user who performed the action
        server_id: ID of the server the action was performed on (if applicable)
        success: Whether the action was successful
        error_message: Error message if action failed
        metadata: Additional metadata about the action
        request: FastAPI request object to extract IP and user agent
    """
    # Extract IP and user agent from request if provided
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
    
    await crud_audit_log.create_audit_log(
        db,
        action=action,
        description=description,
        user_id=user_id,
        server_id=server_id,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        error_message=error_message,
        metadata=metadata,
    )

