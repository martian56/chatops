from app.db.base import AsyncSessionLocal


async def get_session() -> AsyncSessionLocal:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        yield session

