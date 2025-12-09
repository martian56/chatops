from fastapi.testclient import TestClient
import uuid


def test_get_alerts_unauthorized(client: TestClient):
    """Test getting alerts without authentication returns 401."""
    response = client.get("/api/v1/alerts")
    
    assert response.status_code == 401


def test_get_alert_thresholds_unauthorized(client: TestClient):
    """Test getting alert thresholds without authentication returns 401."""
    response = client.get("/api/v1/alerts/thresholds")
    
    assert response.status_code == 401


def test_get_alert_by_id_unauthorized(client: TestClient):
    """Test getting alert by ID without authentication returns 401."""
    alert_id = uuid.uuid4()
    
    response = client.get(f"/api/v1/alerts/{alert_id}")
    
    assert response.status_code == 401


def test_create_alert_threshold_unauthorized(client: TestClient):
    """Test creating alert threshold without authentication returns 401."""
    threshold_data = {
        "server_id": str(uuid.uuid4()),
        "metric_type": "cpu_usage_percent",
        "threshold_value": 80.0,
        "comparison": "gt",
        "enabled": True
    }
    
    response = client.post("/api/v1/alerts/thresholds", json=threshold_data)
    
    assert response.status_code == 401


def test_update_alert_threshold_unauthorized(client: TestClient):
    """Test updating alert threshold without authentication returns 401."""
    threshold_id = uuid.uuid4()
    update_data = {"threshold_value": 90.0}
    
    response = client.put(f"/api/v1/alerts/thresholds/{threshold_id}", json=update_data)
    
    assert response.status_code == 401


def test_delete_alert_threshold_unauthorized(client: TestClient):
    """Test deleting alert threshold without authentication returns 401."""
    threshold_id = uuid.uuid4()
    
    response = client.delete(f"/api/v1/alerts/thresholds/{threshold_id}")
    
    assert response.status_code == 401


def test_resolve_alert_unauthorized(client: TestClient):
    """Test resolving alert without authentication returns 401."""
    alert_id = uuid.uuid4()
    
    response = client.post(f"/api/v1/alerts/{alert_id}/resolve")
    
    assert response.status_code == 401

