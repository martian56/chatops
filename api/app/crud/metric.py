from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
from app.models.metric import Metric


async def create_metric(db: AsyncSession, server_id: uuid.UUID, metrics_data: dict) -> Metric:
    """Create a new metric entry"""
    cpu = metrics_data.get("cpu", {})
    memory = metrics_data.get("memory", {})
    disk = metrics_data.get("disk", {})
    network = metrics_data.get("network", {})
    
    # Extract containers and processes for extra_data
    extra_data = {
        "containers": metrics_data.get("containers", []),
        "processes": metrics_data.get("processes", []),
    }
    
    metric = Metric(
        server_id=server_id,
        timestamp=metrics_data.get("timestamp", datetime.utcnow()),
        cpu_usage_percent=cpu.get("usage_percent", 0.0),
        cpu_cores=cpu.get("cores"),
        cpu_frequency_mhz=cpu.get("frequency_mhz"),
        memory_total_gb=memory.get("total_gb", 0.0),
        memory_used_gb=memory.get("used_gb", 0.0),
        memory_available_gb=memory.get("available_gb", 0.0),
        memory_usage_percent=memory.get("usage_percent", 0.0),
        disk_total_gb=disk.get("total_gb", 0.0),
        disk_used_gb=disk.get("used_gb", 0.0),
        disk_available_gb=disk.get("available_gb", 0.0),
        disk_usage_percent=disk.get("usage_percent", 0.0),
        network_bytes_sent=network.get("bytes_sent"),
        network_bytes_recv=network.get("bytes_recv"),
        network_packets_sent=network.get("packets_sent"),
        network_packets_recv=network.get("packets_recv"),
        extra_data=extra_data,
    )
    
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric


async def get_metrics(
    db: AsyncSession,
    server_id: uuid.UUID,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
) -> List[Metric]:
    """Get metrics for a server within a time range"""
    query = select(Metric).where(Metric.server_id == server_id)
    
    if start_time:
        query = query.where(Metric.timestamp >= start_time)
    if end_time:
        query = query.where(Metric.timestamp <= end_time)
    
    query = query.order_by(desc(Metric.timestamp)).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_latest_metric(db: AsyncSession, server_id: uuid.UUID) -> Optional[Metric]:
    """Get the latest metric for a server"""
    query = (
        select(Metric)
        .where(Metric.server_id == server_id)
        .order_by(desc(Metric.timestamp))
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def delete_old_metrics(db: AsyncSession, older_than_days: int = 30) -> int:
    """Delete metrics older than specified days. Returns count of deleted records."""
    cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
    query = select(Metric).where(Metric.timestamp < cutoff_date)
    result = await db.execute(query)
    metrics_to_delete = result.scalars().all()
    count = len(metrics_to_delete)
    
    for metric in metrics_to_delete:
        await db.delete(metric)
    
    await db.commit()
    return count

