from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.models.connection_event import ConnectionEventType


class ConnectionEventBase(BaseModel):
    event_type: ConnectionEventType
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
    extra_data: Optional[str] = None


class ConnectionEventCreate(ConnectionEventBase):
    server_id: uuid.UUID
    timestamp: Optional[datetime] = None


class ConnectionEventResponse(ConnectionEventBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    server_id: uuid.UUID
    timestamp: datetime

