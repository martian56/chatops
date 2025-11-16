from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid
from app.models.alert import Alert, AlertThreshold
from app.schemas.alert import AlertCreate, AlertThresholdCreate, AlertThresholdUpdate
from app.crud import api_key as crud_api_key


# Alert CRUD
async def get_alert(
    db: AsyncSession, 
    alert_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
) -> Optional[Alert]:
    """Get alert by ID - if user_id is provided, verify ownership"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if alert and user_id:
        # Verify that the alert belongs to a server owned by the user
        user_server_ids = await crud_api_key.get_user_server_ids(db, user_id)
        if alert.server_id not in user_server_ids:
            return None
    
    return alert


async def get_alerts(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    resolved: Optional[bool] = None,
    user_id: Optional[uuid.UUID] = None
) -> List[Alert]:
    """Get all alerts, optionally filtered by resolved status and user's servers"""
    query = select(Alert)
    
    if user_id:
        # Filter by user's servers
        user_server_ids = await crud_api_key.get_user_server_ids(db, user_id)
        if not user_server_ids:
            return []
        query = query.where(Alert.server_id.in_(user_server_ids))
    
    if resolved is not None:
        query = query.where(Alert.resolved == resolved)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_alert(db: AsyncSession, alert_in: AlertCreate) -> Alert:
    """Create a new alert"""
    db_alert = Alert(**alert_in.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


async def resolve_alert(db: AsyncSession, alert_id: uuid.UUID) -> Optional[Alert]:
    """Resolve an alert"""
    db_alert = await get_alert(db, alert_id)
    if not db_alert:
        return None
    
    db_alert.resolved = True
    from datetime import datetime
    db_alert.resolved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


# AlertThreshold CRUD
async def get_alert_threshold(
    db: AsyncSession, 
    threshold_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = None
) -> Optional[AlertThreshold]:
    """Get alert threshold by ID - if user_id is provided, verify ownership"""
    result = await db.execute(
        select(AlertThreshold).where(AlertThreshold.id == threshold_id)
    )
    threshold = result.scalar_one_or_none()
    
    if threshold and user_id:
        # Verify that the threshold belongs to a server owned by the user
        user_server_ids = await crud_api_key.get_user_server_ids(db, user_id)
        if threshold.server_id not in user_server_ids:
            return None
    
    return threshold


async def get_alert_thresholds(
    db: AsyncSession, 
    server_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None
) -> List[AlertThreshold]:
    """Get all alert thresholds, optionally filtered by server and user's servers"""
    query = select(AlertThreshold)
    
    if user_id:
        # Filter by user's servers
        user_server_ids = await crud_api_key.get_user_server_ids(db, user_id)
        if not user_server_ids:
            return []
        query = query.where(AlertThreshold.server_id.in_(user_server_ids))
    
    if server_id:
        query = query.where(AlertThreshold.server_id == server_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_alert_threshold(
    db: AsyncSession, threshold_in: AlertThresholdCreate
) -> AlertThreshold:
    """Create a new alert threshold"""
    db_threshold = AlertThreshold(**threshold_in.model_dump())
    db.add(db_threshold)
    await db.commit()
    await db.refresh(db_threshold)
    return db_threshold


async def update_alert_threshold(
    db: AsyncSession, threshold_id: uuid.UUID, threshold_in: AlertThresholdUpdate
) -> Optional[AlertThreshold]:
    """Update alert threshold"""
    db_threshold = await get_alert_threshold(db, threshold_id)
    if not db_threshold:
        return None
    
    update_data = threshold_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_threshold, field, value)
    
    await db.commit()
    await db.refresh(db_threshold)
    return db_threshold


async def delete_alert_threshold(db: AsyncSession, threshold_id: uuid.UUID) -> bool:
    """Delete alert threshold"""
    db_threshold = await get_alert_threshold(db, threshold_id)
    if not db_threshold:
        return False
    
    await db.delete(db_threshold)
    await db.commit()
    return True

