from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
from datetime import datetime
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user, get_current_user_or_api_key
from app.models.user import User
from app.crud import server as crud_server
from app.services.ws_manager import ws_manager
from pydantic import BaseModel

router = APIRouter()

# In-memory cache for metrics (server_id -> latest metrics)
metrics_cache: Dict[str, dict] = {}


class ServerMetrics(BaseModel):
    server_id: uuid.UUID
    timestamp: datetime
    cpu: dict
    memory: dict
    disk: dict
    network: dict


class MetricsCreate(BaseModel):
    """Metrics sent from agent"""
    server_id: str
    timestamp: datetime
    cpu: dict
    memory: dict
    disk: dict
    network: dict


@router.post("", status_code=status.HTTP_201_CREATED)
async def receive_metrics(
    metrics: MetricsCreate,
    auth = Depends(get_current_user_or_api_key),
):
    """Receive metrics from an agent (API key auth)"""
    server_id_str = str(metrics.server_id)
    
    # Convert to dict for caching
    metrics_dict = {
        "server_id": metrics.server_id,
        "timestamp": metrics.timestamp,
        "cpu": metrics.cpu,
        "memory": metrics.memory,
        "disk": metrics.disk,
        "network": metrics.network,
    }
    
    # Store in cache
    metrics_cache[server_id_str] = metrics_dict
    
    # Broadcast via WebSocket
    await ws_manager.send_metrics(server_id_str, metrics_dict)
    
    return {"status": "ok", "message": "Metrics received"}


@router.post("/{server_id}", status_code=status.HTTP_201_CREATED)
async def receive_metrics_by_id(
    server_id: uuid.UUID,
    metrics: MetricsCreate,
    auth = Depends(get_current_user_or_api_key),
):
    """Receive metrics from an agent (endpoint with server_id in path)"""
    # Use server_id from path (more reliable)
    server_id_str = str(server_id)
    
    # Convert to dict for caching
    metrics_dict = {
        "server_id": server_id_str,
        "timestamp": metrics.timestamp,
        "cpu": metrics.cpu,
        "memory": metrics.memory,
        "disk": metrics.disk,
        "network": metrics.network,
    }
    
    # Store in cache
    metrics_cache[server_id_str] = metrics_dict
    
    # Broadcast via WebSocket
    await ws_manager.send_metrics(server_id_str, metrics_dict)
    
    return {"status": "ok", "message": "Metrics received"}


@router.get("/{server_id}/latest")
async def get_latest_metrics(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get latest metrics for a server"""
    server = await crud_server.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    server_id_str = str(server_id)
    if server_id_str not in metrics_cache:
        raise HTTPException(
            status_code=404,
            detail="No metrics available for this server"
        )
    
    return metrics_cache[server_id_str]


@router.get("/{server_id}/history")
async def get_metrics_history(
    server_id: uuid.UUID,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get metrics history for a server"""
    server = await crud_server.get_server(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # TODO: Get actual metrics history from database/cache
    raise HTTPException(
        status_code=501,
        detail="Metrics history endpoint not yet implemented - requires agent connection",
    )

