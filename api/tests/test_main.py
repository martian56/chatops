from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "ChatOps API"
    assert "version" in data
    assert data["version"] == "1.0.0"
    assert "docs" in data


def test_health_check_get(client: TestClient):
    """Test health check endpoint with GET."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_health_check_head(client: TestClient):
    """Test health check endpoint with HEAD."""
    response = client.head("/health")
    
    assert response.status_code == 200
    assert response.content == b""
