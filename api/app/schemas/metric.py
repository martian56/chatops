from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class MetricBase(BaseModel):
    cpu_usage_percent: float
    cpu_cores: Optional[float] = None
    cpu_frequency_mhz: Optional[float] = None
    memory_total_gb: float
    memory_used_gb: float
    memory_available_gb: float
    memory_usage_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_available_gb: float
    disk_usage_percent: float
    network_bytes_sent: Optional[float] = None
    network_bytes_recv: Optional[float] = None
    network_packets_sent: Optional[float] = None
    network_packets_recv: Optional[float] = None
    extra_data: Optional[Dict[str, Any]] = None


class MetricCreate(MetricBase):
    server_id: uuid.UUID
    timestamp: Optional[datetime] = None


class MetricResponse(MetricBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    server_id: uuid.UUID
    timestamp: datetime
    created_at: datetime

