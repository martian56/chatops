from fastapi.testclient import TestClient


def test_get_servers_unauthorized(client: TestClient):
    """Test that accessing servers without authentication returns 401."""
    response = client.get("/api/v1/servers")
    
    assert response.status_code == 401


def test_create_server_unauthorized(client: TestClient):
    """Test creating server without authentication returns 401."""
    server_data = {
        "name": "Test Server",
        "host": "192.168.1.100",
        "port": 22
    }
    
    response = client.post("/api/v1/servers", json=server_data)
    
    assert response.status_code == 401


def test_get_server_by_id_unauthorized(client: TestClient):
    """Test getting server by ID without authentication returns 401."""
    import uuid
    fake_id = uuid.uuid4()
    
    response = client.get(f"/api/v1/servers/{fake_id}")
    
    assert response.status_code == 401


def test_update_server_unauthorized(client: TestClient):
    """Test updating server without authentication returns 401."""
    import uuid
    fake_id = uuid.uuid4()
    
    update_data = {
        "name": "Updated Name"
    }
    
    response = client.put(f"/api/v1/servers/{fake_id}", json=update_data)
    
    assert response.status_code == 401


def test_delete_server_unauthorized(client: TestClient):
    """Test deleting server without authentication returns 401."""
    import uuid
    fake_id = uuid.uuid4()
    
    response = client.delete(f"/api/v1/servers/{fake_id}")
    
    assert response.status_code == 401
