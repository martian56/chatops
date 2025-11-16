from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.models.command_history import CommandStatus


class CommandHistoryBase(BaseModel):
    command: str
    working_directory: Optional[str] = None
    status: CommandStatus = CommandStatus.PENDING


class CommandHistoryCreate(CommandHistoryBase):
    server_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None


class CommandHistoryUpdate(BaseModel):
    status: Optional[CommandStatus] = None
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error_message: Optional[str] = None


class CommandHistoryResponse(CommandHistoryBase):
    id: uuid.UUID
    server_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    exit_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    error_message: Optional[str]

    class Config:
        from_attributes = True

