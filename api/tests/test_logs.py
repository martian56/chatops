from fastapi.testclient import TestClient
import uuid


def test_get_server_logs_unauthorized(client: TestClient):
    """Test getting server logs without authentication returns 401."""
    server_id = uuid.uuid4()
    
    response = client.get(f"/api/v1/logs/{server_id}")
    
    assert response.status_code == 401

