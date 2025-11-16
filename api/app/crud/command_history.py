from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from app.models.command_history import CommandHistory, CommandStatus


async def create_command_history(
    db: AsyncSession,
    server_id: uuid.UUID,
    command: str,
    user_id: Optional[uuid.UUID] = None,
    working_directory: Optional[str] = None,
    status: CommandStatus = CommandStatus.PENDING,
) -> CommandHistory:
    """Create a new command history entry"""
    cmd_history = CommandHistory(
        server_id=server_id,
        user_id=user_id,
        command=command,
        working_directory=working_directory,
        status=status,
    )
    
    db.add(cmd_history)
    await db.commit()
    await db.refresh(cmd_history)
    return cmd_history


async def update_command_history(
    db: AsyncSession,
    command_id: uuid.UUID,
    status: Optional[CommandStatus] = None,
    exit_code: Optional[int] = None,
    stdout: Optional[str] = None,
    stderr: Optional[str] = None,
    error_message: Optional[str] = None,
) -> Optional[CommandHistory]:
    """Update a command history entry"""
    cmd_history = await db.get(CommandHistory, command_id)
    if not cmd_history:
        return None
    
    if status:
        cmd_history.status = status
    if exit_code is not None:
        cmd_history.exit_code = exit_code
    if stdout is not None:
        cmd_history.stdout = stdout
    if stderr is not None:
        cmd_history.stderr = stderr
    if error_message is not None:
        cmd_history.error_message = error_message
    
    # Calculate duration if completing
    if status in [CommandStatus.COMPLETED, CommandStatus.FAILED, CommandStatus.TIMEOUT]:
        cmd_history.completed_at = datetime.now(timezone.utc)
        if cmd_history.started_at:
            duration = (cmd_history.completed_at - cmd_history.started_at).total_seconds() * 1000
            cmd_history.duration_ms = int(duration)
    
    await db.commit()
    await db.refresh(cmd_history)
    return cmd_history


async def get_command_history(
    db: AsyncSession,
    server_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    status: Optional[CommandStatus] = None,
    limit: int = 100,
) -> List[CommandHistory]:
    """Get command history with filters"""
    query = select(CommandHistory)
    
    if server_id:
        query = query.where(CommandHistory.server_id == server_id)
    if user_id:
        query = query.where(CommandHistory.user_id == user_id)
    if status:
        query = query.where(CommandHistory.status == status)
    
    query = query.order_by(desc(CommandHistory.started_at)).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())

