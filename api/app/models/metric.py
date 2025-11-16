from sqlalchemy import Column, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Metric(Base):
    """Time-series metrics data for servers"""
    __tablename__ = "metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    
    # CPU metrics
    cpu_usage_percent = Column(Float, nullable=False)
    cpu_cores = Column(Float, nullable=True)
    cpu_frequency_mhz = Column(Float, nullable=True)
    
    # Memory metrics
    memory_total_gb = Column(Float, nullable=False)
    memory_used_gb = Column(Float, nullable=False)
    memory_available_gb = Column(Float, nullable=False)
    memory_usage_percent = Column(Float, nullable=False)
    
    # Disk metrics
    disk_total_gb = Column(Float, nullable=False)
    disk_used_gb = Column(Float, nullable=False)
    disk_available_gb = Column(Float, nullable=False)
    disk_usage_percent = Column(Float, nullable=False)
    
    # Network metrics
    network_bytes_sent = Column(Float, nullable=True)
    network_bytes_recv = Column(Float, nullable=True)
    network_packets_sent = Column(Float, nullable=True)
    network_packets_recv = Column(Float, nullable=True)
    
    # Additional data (containers, processes, etc.)
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship - passive_deletes=True lets database handle CASCADE
    server = relationship("Server", backref="metrics", passive_deletes=True)

    # Composite index for efficient time-series queries
    __table_args__ = (
        Index('idx_metrics_server_timestamp', 'server_id', 'timestamp'),
    )

