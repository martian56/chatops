from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import uuid
from app.models.alert import Alert, AlertThreshold
from app.schemas.alert import AlertCreate, AlertThresholdCreate, AlertThresholdUpdate


# Alert CRUD
async def get_alert(db: AsyncSession, alert_id: uuid.UUID) -> Optional[Alert]:
    """Get alert by ID"""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    return result.scalar_one_or_none()


async def get_alerts(
    db: AsyncSession, skip: int = 0, limit: int = 100, resolved: Optional[bool] = None
) -> List[Alert]:
    """Get all alerts, optionally filtered by resolved status"""
    query = select(Alert)
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
    db: AsyncSession, threshold_id: uuid.UUID
) -> Optional[AlertThreshold]:
    """Get alert threshold by ID"""
    result = await db.execute(
        select(AlertThreshold).where(AlertThreshold.id == threshold_id)
    )
    return result.scalar_one_or_none()


async def get_alert_thresholds(
    db: AsyncSession, server_id: Optional[uuid.UUID] = None
) -> List[AlertThreshold]:
    """Get all alert thresholds, optionally filtered by server"""
    query = select(AlertThreshold)
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

