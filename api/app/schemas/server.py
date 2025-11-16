from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from app.models.server import ServerStatus, HealthStatus


class ServerBase(BaseModel):
    name: str
    host: Optional[str] = None
    port: Optional[int] = None
    server_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Production Server",
                "host": "192.168.1.100",
                "port": 8080,
                "metadata": {}
            }
        }


class ServerCreate(ServerBase):
    pass


class ServerUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    server_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    
    class Config:
        populate_by_name = True


class ServerResponse(ServerBase):
    id: uuid.UUID
    status: ServerStatus
    health_status: HealthStatus
    last_seen: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class Server(ServerResponse):
    pass

