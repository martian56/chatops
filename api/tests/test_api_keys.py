from fastapi.testclient import TestClient
import uuid


def test_get_my_api_key_info_unauthorized(client: TestClient):
    """Test getting API key info without authentication returns 401."""
    response = client.get("/api/v1/api-keys/me")
    
    assert response.status_code == 401


def test_create_api_key_unauthorized(client: TestClient):
    """Test creating API key without authentication returns 401."""
    api_key_data = {
        "server_id": str(uuid.uuid4()),
        "name": "Test API Key"
    }
    
    response = client.post("/api/v1/api-keys", json=api_key_data)
    
    assert response.status_code == 401


def test_revoke_api_key_unauthorized(client: TestClient):
    """Test revoking API key without authentication returns 401."""
    api_key_id = uuid.uuid4()
    
    response = client.delete(f"/api/v1/api-keys/{api_key_id}")
    
    assert response.status_code == 401

