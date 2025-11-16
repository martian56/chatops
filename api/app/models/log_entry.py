from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class LogLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogSource(str, enum.Enum):
    SYSTEM = "system"
    AGENT = "agent"
    APPLICATION = "application"
    ALERT = "alert"


class LogEntry(Base):
    """Persistent log entries from servers and system"""
    __tablename__ = "log_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    level = Column(SQLEnum(LogLevel), nullable=False, index=True, default=LogLevel.INFO)
    source = Column(SQLEnum(LogSource), nullable=False, default=LogSource.SYSTEM)
    message = Column(Text, nullable=False)
    component = Column(String, nullable=True)  # e.g., "docker", "metrics", "terminal"
    extra_data = Column(Text, nullable=True)  # JSON string for additional context

    # Relationship
    server = relationship("Server", backref="log_entries")

