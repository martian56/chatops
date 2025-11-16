from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.command_history import CommandStatus
from app.crud import server as crud_server
from app.crud import command_history as crud_command_history
from pydantic import BaseModel

router = APIRouter()


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: Optional[int] = None


@router.post("/{server_id}", response_model=CommandResponse)
async def execute_command(
    server_id: uuid.UUID,
    command_req: CommandRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute a command on a server"""
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Create command history entry
    cmd_history = await crud_command_history.create_command_history(
        db,
        server_id=server_id,
        command=command_req.command,
        user_id=current_user.id,
        status=CommandStatus.RUNNING,
    )
    
    # Send command to agent via WebSocket
    from app.services.agent_manager import agent_manager
    
    server_id_str = str(server_id)
    command = {
        "type": "execute_command",
        "command": command_req.command,
    }
    
    response = await agent_manager.send_command(server_id_str, command)
    
    if response is None:
        # Update command history as failed
        await crud_command_history.update_command_history(
            db,
            command_id=cmd_history.id,
            status=CommandStatus.FAILED,
            error_message="Agent not connected",
        )
        raise HTTPException(
            status_code=503,
            detail="Agent not connected. Please ensure the agent is running and connected.",
        )
    
    if "error" in response:
        # Update command history as failed
        await crud_command_history.update_command_history(
            db,
            command_id=cmd_history.id,
            status=CommandStatus.FAILED,
            error_message=response["error"],
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute command: {response['error']}",
        )
    
    if response.get("type") == "command_result":
        result_data = response.get("data", {})
        output = result_data.get("output", "")
        exit_code = result_data.get("exit_code", 0)
        success = exit_code == 0
        
        # Update command history with result
        await crud_command_history.update_command_history(
            db,
            command_id=cmd_history.id,
            status=CommandStatus.COMPLETED if success else CommandStatus.FAILED,
            exit_code=exit_code,
            stdout=output if success else None,
            stderr=output if not success else None,
        )
        
        return CommandResponse(
            success=success,
            output=output,
            exit_code=exit_code,
            error=None if success else output,
        )
    elif response.get("type") == "error":
        # Update command history as failed
        await crud_command_history.update_command_history(
            db,
            command_id=cmd_history.id,
            status=CommandStatus.FAILED,
            error_message=response.get("message", "Unknown error"),
        )
        raise HTTPException(
            status_code=500,
            detail=response.get("message", "Unknown error"),
        )
    else:
        # Update command history as failed
        await crud_command_history.update_command_history(
            db,
            command_id=cmd_history.id,
            status=CommandStatus.FAILED,
            error_message="Unexpected response from agent",
        )
        raise HTTPException(
            status_code=500,
            detail="Unexpected response from agent",
        )

