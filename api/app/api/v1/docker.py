from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.audit_log import AuditAction
from app.models.log_entry import LogLevel, LogSource
from app.crud import server as crud_server
from app.crud import log_entry as crud_log_entry
from app.api.v1.metrics import metrics_cache
from app.services.audit_service import log_audit
from pydantic import BaseModel

router = APIRouter()


class DockerContainer(BaseModel):
    id: str
    name: str
    image: str
    status: str
    state: str
    created: str
    ports: List[dict]


@router.get("/{server_id}/containers", response_model=List[DockerContainer])
async def get_containers(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Docker containers for a server (from metrics cache)"""
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Get containers from metrics cache
    server_id_str = str(server_id)
    if server_id_str not in metrics_cache:
        # Return empty list if no metrics available yet
        return []
    
    metrics = metrics_cache[server_id_str]
    containers = metrics.get("containers", [])
    
    # Convert to DockerContainer format
    result = []
    for container in containers:
        result.append(DockerContainer(
            id=container.get("id", ""),
            name=container.get("name", ""),
            image=container.get("image", ""),
            status=container.get("status", ""),
            state=container.get("state", ""),
            created=container.get("created", ""),
            ports=container.get("ports", []),
        ))
    
    return result


@router.post("/{server_id}/containers/{container_id}/start")
async def start_container(
    server_id: uuid.UUID,
    container_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a Docker container"""
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Send command to agent via WebSocket
    from app.services.agent_manager import agent_manager
    
    server_id_str = str(server_id)
    command = {
        "type": "start_container",
        "container_id": container_id,
    }
    
    response = await agent_manager.send_command(server_id_str, command)
    
    if response is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not connected. Please ensure the agent is running and connected.",
        )
    
    if "error" in response:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start container: {response['error']}",
        )
    
    if response.get("type") == "container_started":
        # Log the action
        await crud_log_entry.create_log_entry(
            db,
            server_id=server_id,
            message=f"Container {container_id[:12]} started by {current_user.username}",
            level=LogLevel.INFO,
            source=LogSource.APPLICATION,
            component="docker",
        )
        
        # Audit log
        await log_audit(
            db,
            action=AuditAction.CONTAINER_STARTED,
            description=f"Started container {container_id[:12]}",
            user_id=current_user.id,
            server_id=server_id,
            metadata={"container_id": container_id},
            request=request,
        )
        
        return {"status": "success", "message": "Container started successfully"}
    elif response.get("type") == "error":
        raise HTTPException(
            status_code=500,
            detail=response.get("message", "Unknown error"),
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Unexpected response from agent",
        )


@router.post("/{server_id}/containers/{container_id}/stop")
async def stop_container(
    server_id: uuid.UUID,
    container_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop a Docker container"""
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Send command to agent via WebSocket
    from app.services.agent_manager import agent_manager
    
    server_id_str = str(server_id)
    command = {
        "type": "stop_container",
        "container_id": container_id,
    }
    
    response = await agent_manager.send_command(server_id_str, command)
    
    if response is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not connected. Please ensure the agent is running and connected.",
        )
    
    if "error" in response:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop container: {response['error']}",
        )
    
    if response.get("type") == "container_stopped":
        # Log the action
        await crud_log_entry.create_log_entry(
            db,
            server_id=server_id,
            message=f"Container {container_id[:12]} stopped by {current_user.username}",
            level=LogLevel.INFO,
            source=LogSource.APPLICATION,
            component="docker",
        )
        
        # Audit log
        await log_audit(
            db,
            action=AuditAction.CONTAINER_STOPPED,
            description=f"Stopped container {container_id[:12]}",
            user_id=current_user.id,
            server_id=server_id,
            metadata={"container_id": container_id},
            request=request,
        )
        
        return {"status": "success", "message": "Container stopped successfully"}
    elif response.get("type") == "error":
        raise HTTPException(
            status_code=500,
            detail=response.get("message", "Unknown error"),
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Unexpected response from agent",
        )


@router.post("/{server_id}/containers/{container_id}/restart")
async def restart_container(
    server_id: uuid.UUID,
    container_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Restart a Docker container"""
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Send command to agent via WebSocket
    from app.services.agent_manager import agent_manager
    
    server_id_str = str(server_id)
    command = {
        "type": "restart_container",
        "container_id": container_id,
    }
    
    response = await agent_manager.send_command(server_id_str, command)
    
    if response is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not connected. Please ensure the agent is running and connected.",
        )
    
    if "error" in response:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart container: {response['error']}",
        )
    
    if response.get("type") == "container_restarted":
        # Log the action
        await crud_log_entry.create_log_entry(
            db,
            server_id=server_id,
            message=f"Container {container_id[:12]} restarted by {current_user.username}",
            level=LogLevel.INFO,
            source=LogSource.APPLICATION,
            component="docker",
        )
        
        # Audit log
        await log_audit(
            db,
            action=AuditAction.CONTAINER_RESTARTED,
            description=f"Restarted container {container_id[:12]}",
            user_id=current_user.id,
            server_id=server_id,
            metadata={"container_id": container_id},
            request=request,
        )
        
        return {"status": "success", "message": "Container restarted successfully"}
    elif response.get("type") == "error":
        raise HTTPException(
            status_code=500,
            detail=response.get("message", "Unknown error"),
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Unexpected response from agent",
        )


@router.get("/{server_id}/containers/{container_id}/logs")
async def get_container_logs(
    server_id: uuid.UUID,
    container_id: str,
    tail: Optional[int] = 500,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get logs for a Docker container"""
    server = await crud_server.get_server(db, server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Send command to agent via WebSocket
    from app.services.agent_manager import agent_manager
    
    server_id_str = str(server_id)
    command = {
        "type": "get_container_logs",
        "container_id": container_id,
        "tail": tail or 500,
    }
    
    response = await agent_manager.send_command(server_id_str, command)
    
    if response is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not connected. Please ensure the agent is running and connected.",
        )
    
    if "error" in response:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get container logs: {response['error']}",
        )
    
    if response.get("type") == "container_logs":
        logs_data = response.get("data", {})
        logs = logs_data.get("logs", [])
        return logs
    elif response.get("type") == "error":
        raise HTTPException(
            status_code=500,
            detail=response.get("message", "Unknown error"),
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="Unexpected response from agent",
        )

