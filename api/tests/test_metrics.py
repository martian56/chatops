from fastapi.testclient import TestClient
import uuid


def test_get_metrics_history_unauthorized(client: TestClient):
    """Test getting metrics history without authentication returns 401."""
    server_id = uuid.uuid4()
    
    response = client.get(f"/api/v1/metrics/{server_id}/history")
    
    assert response.status_code == 401

