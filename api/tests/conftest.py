import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app
from app.db.base import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from app.crud.user import create_user
from app.schemas.user import UserCreate
from datetime import timedelta
import uuid


# Test database URL - use in-memory SQLite or separate test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session and tables for each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """TestClient fixture with overridden database dependency."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user_data = UserCreate(
        email="testuser@example.com",
        username="testuser",
        password="TestPassword123!",
        password_confirm="TestPassword123!",
        full_name="Test User"
    )
    user = await create_user(db_session, user_data)
    return user


@pytest.fixture
async def test_user_2(db_session: AsyncSession) -> User:
    """Create a second test user for multi-user tests."""
    user_data = UserCreate(
        email="testuser2@example.com",
        username="testuser2",
        password="TestPassword123!",
        password_confirm="TestPassword123!",
        full_name="Test User Two"
    )
    user = await create_user(db_session, user_data)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Generate valid access token for test user."""
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(minutes=30),
    )
    return access_token


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Generate authorization headers with valid token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def auth_token_2(test_user_2: User) -> str:
    """Generate valid access token for second test user."""
    access_token = create_access_token(
        data={"sub": str(test_user_2.id), "email": test_user_2.email},
        expires_delta=timedelta(minutes=30),
    )
    return access_token


@pytest.fixture
def auth_headers_2(auth_token_2: str) -> dict:
    """Generate authorization headers for second test user."""
    return {"Authorization": f"Bearer {auth_token_2}"}
