from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class AuditAction(str, enum.Enum):
    # Server actions
    SERVER_CREATED = "server_created"
    SERVER_UPDATED = "server_updated"
    SERVER_DELETED = "server_deleted"
    
    # API Key actions
    API_KEY_CREATED = "api_key_created"
    API_KEY_DELETED = "api_key_deleted"
    API_KEY_DEACTIVATED = "api_key_deactivated"
    API_KEY_USED = "api_key_used"
    
    # Alert actions
    ALERT_CREATED = "alert_created"
    ALERT_RESOLVED = "alert_resolved"
    THRESHOLD_CREATED = "threshold_created"
    THRESHOLD_UPDATED = "threshold_updated"
    THRESHOLD_DELETED = "threshold_deleted"
    
    # Docker actions
    CONTAINER_STARTED = "container_started"
    CONTAINER_STOPPED = "container_stopped"
    CONTAINER_RESTARTED = "container_restarted"
    
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    PASSWORD_CHANGED = "password_changed"
    
    # System actions
    SETTINGS_UPDATED = "settings_updated"


class AuditLog(Base):
    """Audit log for tracking user actions and system events"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    server_id = Column(UUID(as_uuid=True), ForeignKey("servers.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    extra_data = Column(JSON, nullable=True)  # Additional context (e.g., what changed)
    success = Column(Boolean, nullable=False, default=True)  # Whether action succeeded
    error_message = Column(Text, nullable=True)

    # Relationships - passive_deletes=True lets database handle CASCADE/SET NULL
    user = relationship("User", backref="audit_logs")
    server = relationship("Server", backref="audit_logs", passive_deletes=True)

