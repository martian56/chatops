from typing import Dict, Optional
from fastapi import WebSocket
import json
import uuid
import asyncio
from collections import defaultdict


class AgentManager:
    """Manage agent WebSocket connections"""
    
    def __init__(self):
        # server_id -> WebSocket
        self.agent_connections: Dict[str, WebSocket] = {}
        # request_id -> asyncio.Queue for responses
        self.response_queues: Dict[str, asyncio.Queue] = {}
    
    def register_agent(self, server_id: str, websocket: WebSocket):
        """Register an agent connection for a server"""
        self.agent_connections[server_id] = websocket
    
    def unregister_agent(self, server_id: str):
        """Unregister an agent connection"""
        if server_id in self.agent_connections:
            del self.agent_connections[server_id]
    
    def get_agent_connection(self, server_id: str) -> Optional[WebSocket]:
        """Get the agent connection for a server"""
        return self.agent_connections.get(server_id)
    
    def create_response_queue(self, request_id: str) -> asyncio.Queue:
        """Create a queue for a request ID"""
        queue = asyncio.Queue()
        self.response_queues[request_id] = queue
        return queue
    
    def put_response(self, request_id: str, response: dict):
        """Put a response in the queue for a request ID"""
        if request_id in self.response_queues:
            self.response_queues[request_id].put_nowait(response)
            del self.response_queues[request_id]
    
    async def send_command(self, server_id: str, command: dict) -> Optional[dict]:
        """Send a command to an agent and wait for response"""
        websocket = self.get_agent_connection(server_id)
        if not websocket:
            return None
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        command["request_id"] = request_id
        
        # Create response queue
        response_queue = self.create_response_queue(request_id)
        
        try:
            # Send command
            await websocket.send_json(command)
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(response_queue.get(), timeout=10.0)
                return response
            except asyncio.TimeoutError:
                # Clean up queue
                if request_id in self.response_queues:
                    del self.response_queues[request_id]
                return {"error": "Timeout waiting for agent response"}
        except Exception as e:
            # Clean up queue
            if request_id in self.response_queues:
                del self.response_queues[request_id]
            return {"error": str(e)}


agent_manager = AgentManager()

