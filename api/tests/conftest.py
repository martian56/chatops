import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """TestClient fixture for FastAPI tests."""
    return TestClient(app)
