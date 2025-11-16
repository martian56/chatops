from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid
from app.models.alert import AlertType, AlertSeverity, ComparisonType


class AlertBase(BaseModel):
    server_id: uuid.UUID
    type: AlertType
    severity: AlertSeverity = AlertSeverity.INFO
    message: str
    threshold: Optional[float] = None
    current_value: Optional[float] = None


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: uuid.UUID
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Alert(AlertResponse):
    pass


class AlertThresholdBase(BaseModel):
    server_id: uuid.UUID
    metric_type: AlertType
    threshold_value: float
    comparison: ComparisonType
    enabled: bool = True


class AlertThresholdCreate(AlertThresholdBase):
    pass


class AlertThresholdUpdate(BaseModel):
    metric_type: Optional[AlertType] = None
    threshold_value: Optional[float] = None
    comparison: Optional[ComparisonType] = None
    enabled: Optional[bool] = None


class AlertThreshold(AlertThresholdBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

