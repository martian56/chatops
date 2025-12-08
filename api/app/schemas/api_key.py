from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid


class APIKeyBase(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    server_id: uuid.UUID


class APIKeyResponse(APIKeyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    server_id: uuid.UUID
    key: str  # Only returned on creation
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime


class APIKeyInfo(APIKeyBase):
    """API key info without the actual key"""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    server_id: uuid.UUID
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime

