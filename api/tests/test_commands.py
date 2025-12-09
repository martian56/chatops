from fastapi.testclient import TestClient
import uuid


def test_execute_command_unauthorized(client: TestClient):
    """Test executing command without authentication returns 401."""
    server_id = uuid.uuid4()
    command_data = {"command": "ls -la"}
    
    response = client.post(f"/api/v1/commands/{server_id}", json=command_data)
    
    assert response.status_code == 401

