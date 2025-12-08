from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from app.models.audit_log import AuditAction


class AuditLogBase(BaseModel):
    action: AuditAction
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    user_id: Optional[uuid.UUID] = None
    server_id: Optional[uuid.UUID] = None
    timestamp: Optional[datetime] = None


class AuditLogResponse(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    server_id: Optional[uuid.UUID]
    timestamp: datetime

