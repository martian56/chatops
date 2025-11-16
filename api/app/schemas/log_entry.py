from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.models.log_entry import LogLevel, LogSource


class LogEntryBase(BaseModel):
    message: str
    level: LogLevel = LogLevel.INFO
    source: LogSource = LogSource.SYSTEM
    component: Optional[str] = None
    extra_data: Optional[str] = None


class LogEntryCreate(LogEntryBase):
    server_id: Optional[uuid.UUID] = None
    timestamp: Optional[datetime] = None


class LogEntryResponse(LogEntryBase):
    id: uuid.UUID
    server_id: Optional[uuid.UUID]
    timestamp: datetime

    class Config:
        from_attributes = True

