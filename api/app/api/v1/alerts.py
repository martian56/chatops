from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.crud import alert as crud_alert
from app.schemas.alert import (
    Alert,
    AlertCreate,
    AlertResponse,
    AlertThreshold,
    AlertThresholdCreate,
    AlertThresholdUpdate,
)

router = APIRouter()


# Alert Thresholds - Must come before /{alert_id} route to avoid path conflicts
@router.get("/thresholds", response_model=List[AlertThreshold])
async def get_alert_thresholds(
    server_id: Optional[uuid.UUID] = Query(None, description="Filter by server ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all alert thresholds for user's servers, optionally filtered by server"""
    thresholds = await crud_alert.get_alert_thresholds(
        db, server_id=server_id, user_id=current_user.id
    )
    return [AlertThreshold.model_validate(t) for t in thresholds]


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    resolved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all alerts for user's servers, optionally filtered by resolved status"""
    alerts = await crud_alert.get_alerts(
        db, skip=skip, limit=limit, resolved=resolved, user_id=current_user.id
    )
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get alert by ID (only if belongs to user's server)"""
    alert = await crud_alert.get_alert(db, alert_id, user_id=current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resolve an alert (only if belongs to user's server)"""
    # Verify ownership first
    alert = await crud_alert.get_alert(db, alert_id, user_id=current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert = await crud_alert.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/thresholds", response_model=AlertThreshold, status_code=status.HTTP_201_CREATED)
async def create_alert_threshold(
    threshold_in: AlertThresholdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new alert threshold (only for user's servers)"""
    # Verify server ownership
    from app.crud import server as crud_server
    server = await crud_server.get_server(db, threshold_in.server_id, user_id=current_user.id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    threshold = await crud_alert.create_alert_threshold(db, threshold_in)
    return AlertThreshold.model_validate(threshold)


@router.put("/thresholds/{threshold_id}", response_model=AlertThreshold)
async def update_alert_threshold(
    threshold_id: uuid.UUID,
    threshold_in: AlertThresholdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update alert threshold (only if belongs to user's server)"""
    # Verify ownership first
    threshold = await crud_alert.get_alert_threshold(db, threshold_id, user_id=current_user.id)
    if not threshold:
        raise HTTPException(status_code=404, detail="Alert threshold not found")
    
    threshold = await crud_alert.update_alert_threshold(db, threshold_id, threshold_in)
    if not threshold:
        raise HTTPException(status_code=404, detail="Alert threshold not found")
    return AlertThreshold.model_validate(threshold)


@router.delete("/thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_threshold(
    threshold_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete alert threshold (only if belongs to user's server)"""
    # Verify ownership first
    threshold = await crud_alert.get_alert_threshold(db, threshold_id, user_id=current_user.id)
    if not threshold:
        raise HTTPException(status_code=404, detail="Alert threshold not found")
    
    success = await crud_alert.delete_alert_threshold(db, threshold_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert threshold not found")
    return None

