from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
from datetime import datetime
from app.crud import alert as crud_alert
from app.schemas.alert import AlertCreate
from app.models.alert import AlertType, AlertSeverity, ComparisonType


async def check_metrics_against_thresholds(
    db: AsyncSession,
    server_id: uuid.UUID,
    metrics: dict,
) -> None:
    """
    Check metrics against alert thresholds and create alerts if thresholds are exceeded.
    This should be called whenever new metrics are received.
    """
    # Get all enabled thresholds for this server
    thresholds = await crud_alert.get_alert_thresholds(db, server_id=server_id)
    enabled_thresholds = [t for t in thresholds if t.enabled]
    
    if not enabled_thresholds:
        return
    
    print(f"Checking {len(enabled_thresholds)} thresholds for server {server_id}")
    
    # Get existing unresolved alerts for this server to avoid duplicates
    # We need to get all unresolved alerts and filter by server_id
    all_existing_alerts = await crud_alert.get_alerts(
        db, skip=0, limit=1000, resolved=False
    )
    existing_alert_keys = {
        (str(a.server_id), a.type): a 
        for a in all_existing_alerts 
        if str(a.server_id) == str(server_id)
    }
    
    # Check each threshold
    for threshold in enabled_thresholds:
        # Get the current metric value based on threshold type
        current_value = None
        metric_data = None
        
        if threshold.metric_type == AlertType.CPU:
            metric_data = metrics.get("cpu", {})
            current_value = metric_data.get("usage_percent")
        elif threshold.metric_type == AlertType.MEMORY:
            metric_data = metrics.get("memory", {})
            current_value = metric_data.get("usage_percent")
        elif threshold.metric_type == AlertType.DISK:
            metric_data = metrics.get("disk", {})
            current_value = metric_data.get("usage_percent")
        elif threshold.metric_type == AlertType.NETWORK:
            # For network, we might want to check bytes sent/recv
            # For now, let's skip network alerts or use a different metric
            continue
        
        if current_value is None:
            print(f"Warning: No current_value for {threshold.metric_type} metric")
            continue
        
        print(f"Checking {threshold.metric_type}: current={current_value:.1f}%, threshold={threshold.comparison.value} {threshold.threshold_value}%")
        
        # Check if threshold is exceeded
        threshold_exceeded = False
        if threshold.comparison == ComparisonType.GT:
            threshold_exceeded = current_value > threshold.threshold_value
        elif threshold.comparison == ComparisonType.LT:
            threshold_exceeded = current_value < threshold.threshold_value
        
        print(f"Threshold exceeded: {threshold_exceeded}")
        
        # Create alert if threshold is exceeded and no unresolved alert exists
        if threshold_exceeded:
            alert_key = (str(server_id), threshold.metric_type)
            if alert_key not in existing_alert_keys:
                print(f"Creating alert for {threshold.metric_type} threshold exceeded")
                # Determine severity based on how far over the threshold
                severity = AlertSeverity.WARNING
                if threshold.comparison == ComparisonType.GT:
                    if current_value > threshold.threshold_value * 1.5:
                        severity = AlertSeverity.CRITICAL
                    elif current_value > threshold.threshold_value * 1.2:
                        severity = AlertSeverity.WARNING
                elif threshold.comparison == ComparisonType.LT:
                    if current_value < threshold.threshold_value * 0.5:
                        severity = AlertSeverity.CRITICAL
                    elif current_value < threshold.threshold_value * 0.8:
                        severity = AlertSeverity.WARNING
                
                # Create alert message
                comparison_str = ">" if threshold.comparison == ComparisonType.GT else "<"
                message = (
                    f"{threshold.metric_type.upper()} usage is {current_value:.1f}%, "
                    f"which exceeds threshold of {comparison_str} {threshold.threshold_value}%"
                )
                
                # Create alert
                alert_create = AlertCreate(
                    server_id=server_id,
                    type=threshold.metric_type,
                    severity=severity,
                    message=message,
                    threshold=threshold.threshold_value,
                    current_value=current_value,
                )
                
                await crud_alert.create_alert(db, alert_create)
                print(f"Alert created successfully for {threshold.metric_type}")
        else:
            # Threshold not exceeded - resolve any existing alerts for this metric type
            alert_key = (str(server_id), threshold.metric_type)
            if alert_key in existing_alert_keys:
                existing_alert = existing_alert_keys[alert_key]
                if not existing_alert.resolved:
                    await crud_alert.resolve_alert(db, existing_alert.id)

