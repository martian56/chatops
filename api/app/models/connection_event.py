from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class ConnectionEventType(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTED = "reconnected"
    AUTHENTICATION_FAILED = "authentication_failed"
    ERROR = "error"


class ConnectionEvent(Base):
    """Agent connection/disconnection events"""
    __tablename__ = "connection_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(SQLEnum(ConnectionEventType), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # For disconnect events, how long was connected
    extra_data = Column(Text, nullable=True)  # JSON string for additional context

    # Relationship
    server = relationship("Server", backref="connection_events")

