from fastapi.testclient import TestClient


def test_get_current_user_unauthorized(client: TestClient):
    """Test that accessing /me without authentication returns 401."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


def test_login_without_credentials(client: TestClient):
    """Test login endpoint without credentials returns validation error."""
    response = client.post("/api/v1/auth/login", data={})
    
    assert response.status_code == 422


def test_register_missing_fields(client: TestClient):
    """Test register endpoint with missing required fields."""
    response = client.post("/api/v1/auth/register", json={})
    
    assert response.status_code == 422


def test_register_password_too_short(client: TestClient):
    """Test register endpoint with password shorter than 8 characters."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "short",
        "password_confirm": "short",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_register_password_mismatch(client: TestClient):
    """Test register endpoint with mismatched passwords."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "password_confirm": "different123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_refresh_token_missing(client: TestClient):
    """Test refresh token endpoint without token."""
    response = client.post("/api/v1/auth/refresh", json={})
    
    assert response.status_code == 422


def test_refresh_token_invalid(client: TestClient):
    """Test refresh token endpoint with invalid token."""
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})
    
    assert response.status_code == 401


def test_logout_unauthorized(client: TestClient):
    """Test logout endpoint without authentication."""
    response = client.post("/api/v1/auth/logout")
    
    assert response.status_code == 401


def test_update_profile_unauthorized(client: TestClient):
    """Test update profile endpoint without authentication."""
    update_data = {"full_name": "New Name"}
    
    response = client.put("/api/v1/auth/me", json=update_data)
    
    assert response.status_code == 401


def test_change_password_unauthorized(client: TestClient):
    """Test change password endpoint without authentication."""
    password_data = {
        "current_password": "oldpass123",
        "new_password": "newpass123",
        "new_password_confirm": "newpass123"
    }
    
    response = client.post("/api/v1/auth/change-password", json=password_data)
    
    assert response.status_code == 401


def test_register_invalid_email(client: TestClient):
    """Test register endpoint with invalid email format."""
    user_data = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "password123",
        "password_confirm": "password123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 422
