from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class APIKeyBase(BaseModel):
    name: Optional[str] = None
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    server_id: uuid.UUID


class APIKeyResponse(APIKeyBase):
    id: uuid.UUID
    server_id: uuid.UUID
    key: str  # Only returned on creation
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyInfo(APIKeyBase):
    """API key info without the actual key"""
    id: uuid.UUID
    server_id: uuid.UUID
    is_active: bool
    last_used: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

