from fastapi.testclient import TestClient
import uuid


def test_get_containers_unauthorized(client: TestClient):
    """Test getting containers without authentication returns 401."""
    server_id = uuid.uuid4()
    
    response = client.get(f"/api/v1/docker/{server_id}/containers")
    
    assert response.status_code == 401


def test_start_container_unauthorized(client: TestClient):
    """Test starting container without authentication returns 401."""
    server_id = uuid.uuid4()
    container_id = "test-container"
    
    response = client.post(f"/api/v1/docker/{server_id}/containers/{container_id}/start")
    
    assert response.status_code == 401


def test_stop_container_unauthorized(client: TestClient):
    """Test stopping container without authentication returns 401."""
    server_id = uuid.uuid4()
    container_id = "test-container"
    
    response = client.post(f"/api/v1/docker/{server_id}/containers/{container_id}/stop")
    
    assert response.status_code == 401


def test_get_container_logs_unauthorized(client: TestClient):
    """Test getting container logs without authentication returns 401."""
    server_id = uuid.uuid4()
    container_id = "test-container"
    
    response = client.get(f"/api/v1/docker/{server_id}/containers/{container_id}/logs")
    
    assert response.status_code == 401

