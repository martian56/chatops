from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime
import uuid


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # server_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, server_id: str):
        """Register a WebSocket connection (WebSocket should already be accepted)"""
        if server_id not in self.active_connections:
            self.active_connections[server_id] = set()
        self.active_connections[server_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, server_id: str):
        """Remove a WebSocket connection"""
        if server_id in self.active_connections:
            self.active_connections[server_id].discard(websocket)
            if not self.active_connections[server_id]:
                del self.active_connections[server_id]
    
    async def send_metrics(self, server_id: str, metrics: dict):
        """Send metrics to all connected clients for a server"""
        if server_id not in self.active_connections:
            return
        
        message = json.dumps({
            "type": "metrics",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        disconnected = set()
        for connection in self.active_connections[server_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, server_id)
    
    async def send_log(self, server_id: str, log_entry: dict):
        """Send a log entry to all connected clients for a server"""
        if server_id not in self.active_connections:
            return
        
        message = json.dumps({
            "type": "log",
            "data": log_entry,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        disconnected = set()
        for connection in self.active_connections[server_id]:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, server_id)


# Global WebSocket manager instance
ws_manager = ConnectionManager()

