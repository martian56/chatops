"""
Tests for server endpoints with authenticated users.
Tests CRUD operations: Create, Read, Update, Delete servers.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.models.user import User


class TestServerCRUD:
    """Test server CRUD operations with authentication"""
    
    async def test_create_server_success(
        self, 
        client: TestClient, 
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """Test creating a server with valid authentication"""
        server_data = {
            "name": "Production Server",
            "host": "192.168.1.100",
            "port": 22,
            "server_metadata": {"environment": "production", "region": "us-east-1"}
        }
        
        response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == server_data["name"]
        assert data["host"] == server_data["host"]
        assert data["port"] == server_data["port"]
        assert data["server_metadata"] == server_data["server_metadata"]
        assert "id" in data
        assert "created_at" in data
        assert data["status"] == "pending"
    
    async def test_create_server_missing_required_fields(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test creating a server without required fields returns validation error"""
        server_data = {
            "name": "Incomplete Server"
            # Missing host and port
        }
        
        response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_create_server_invalid_port(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test creating a server with invalid port number"""
        server_data = {
            "name": "Bad Port Server",
            "host": "192.168.1.100",
            "port": 99999  # Invalid port
        }
        
        response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_get_servers_empty(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test getting servers when user has none"""
        response = client.get("/api/v1/servers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_get_servers_list(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test getting list of servers after creating them"""
        # Create multiple servers
        server_names = ["Server 1", "Server 2", "Server 3"]
        for name in server_names:
            server_data = {
                "name": name,
                "host": "192.168.1.100",
                "port": 22
            }
            client.post("/api/v1/servers", json=server_data, headers=auth_headers)
        
        # Get all servers
        response = client.get("/api/v1/servers", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(s["name"] in server_names for s in data)
    
    async def test_get_servers_pagination(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test server list pagination"""
        # Create 5 servers
        for i in range(5):
            server_data = {
                "name": f"Server {i}",
                "host": "192.168.1.100",
                "port": 22
            }
            client.post("/api/v1/servers", json=server_data, headers=auth_headers)
        
        # Test skip and limit
        response = client.get("/api/v1/servers?skip=2&limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    async def test_get_server_by_id(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test getting a specific server by ID"""
        # Create a server
        server_data = {
            "name": "Test Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # Get server by ID
        response = client.get(f"/api/v1/servers/{server_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == server_id
        assert data["name"] == server_data["name"]
    
    async def test_get_server_not_found(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test getting non-existent server returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = client.get(f"/api/v1/servers/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Server not found"
    
    async def test_get_server_different_user(
        self, 
        client: TestClient, 
        auth_headers: dict,
        auth_headers_2: dict
    ):
        """Test that users cannot access other users' servers"""
        # User 1 creates a server
        server_data = {
            "name": "User 1 Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # User 2 tries to access User 1's server
        response = client.get(
            f"/api/v1/servers/{server_id}",
            headers=auth_headers_2
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Server not found"
    
    async def test_update_server_success(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test updating a server"""
        # Create a server
        server_data = {
            "name": "Original Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # Update the server
        update_data = {
            "name": "Updated Server",
            "host": "192.168.1.101",
            "port": 2222
        }
        response = client.put(
            f"/api/v1/servers/{server_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["host"] == update_data["host"]
        assert data["port"] == update_data["port"]
        assert data["id"] == server_id
    
    async def test_update_server_partial(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test partial update of a server (only some fields)"""
        # Create a server
        server_data = {
            "name": "Original Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        original_host = create_response.json()["host"]
        
        # Update only the name
        update_data = {"name": "New Name Only"}
        response = client.put(
            f"/api/v1/servers/{server_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["host"] == original_host  # Should remain unchanged
    
    async def test_update_server_not_found(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test updating non-existent server returns 404"""
        fake_id = str(uuid.uuid4())
        update_data = {"name": "Updated"}
        
        response = client.put(
            f"/api/v1/servers/{fake_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_update_server_different_user(
        self, 
        client: TestClient, 
        auth_headers: dict,
        auth_headers_2: dict
    ):
        """Test that users cannot update other users' servers"""
        # User 1 creates a server
        server_data = {
            "name": "User 1 Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # User 2 tries to update User 1's server
        update_data = {"name": "Hacked!"}
        response = client.put(
            f"/api/v1/servers/{server_id}",
            json=update_data,
            headers=auth_headers_2
        )
        
        assert response.status_code == 404
    
    async def test_delete_server_success(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test deleting a server"""
        # Create a server
        server_data = {
            "name": "Server to Delete",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # Delete the server
        response = client.delete(
            f"/api/v1/servers/{server_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify server is deleted
        get_response = client.get(
            f"/api/v1/servers/{server_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    async def test_delete_server_not_found(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test deleting non-existent server returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = client.delete(
            f"/api/v1/servers/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_delete_server_different_user(
        self, 
        client: TestClient, 
        auth_headers: dict,
        auth_headers_2: dict
    ):
        """Test that users cannot delete other users' servers"""
        # User 1 creates a server
        server_data = {
            "name": "User 1 Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # User 2 tries to delete User 1's server
        response = client.delete(
            f"/api/v1/servers/{server_id}",
            headers=auth_headers_2
        )
        
        assert response.status_code == 404
        
        # Verify server still exists for User 1
        get_response = client.get(
            f"/api/v1/servers/{server_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
    
    async def test_check_server_health(
        self, 
        client: TestClient, 
        auth_headers: dict
    ):
        """Test server health check endpoint"""
        # Create a server
        server_data = {
            "name": "Health Check Server",
            "host": "192.168.1.100",
            "port": 22
        }
        create_response = client.post(
            "/api/v1/servers",
            json=server_data,
            headers=auth_headers
        )
        server_id = create_response.json()["id"]
        
        # Check health
        response = client.post(
            f"/api/v1/servers/{server_id}/health",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data


class TestServerIsolation:
    """Test that servers are properly isolated between users"""
    
    async def test_users_see_only_own_servers(
        self, 
        client: TestClient, 
        auth_headers: dict,
        auth_headers_2: dict
    ):
        """Test that users only see their own servers in list"""
        # User 1 creates 2 servers
        for i in range(2):
            server_data = {
                "name": f"User 1 Server {i}",
                "host": "192.168.1.100",
                "port": 22
            }
            client.post("/api/v1/servers", json=server_data, headers=auth_headers)
        
        # User 2 creates 3 servers
        for i in range(3):
            server_data = {
                "name": f"User 2 Server {i}",
                "host": "192.168.1.101",
                "port": 22
            }
            client.post("/api/v1/servers", json=server_data, headers=auth_headers_2)
        
        # User 1 should see only their 2 servers
        response1 = client.get("/api/v1/servers", headers=auth_headers)
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 2
        assert all("User 1" in s["name"] for s in data1)
        
        # User 2 should see only their 3 servers
        response2 = client.get("/api/v1/servers", headers=auth_headers_2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 3
        assert all("User 2" in s["name"] for s in data2)
