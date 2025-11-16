from app.db.base import engine, Base
from app.models import (
    user,
    server,
    alert,
    api_key,
    metric,
    log_entry,
    command_history,
    connection_event,
    audit_log,
)  # noqa: F401


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

