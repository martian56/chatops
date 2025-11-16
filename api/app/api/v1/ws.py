from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.ws_manager import ws_manager
from app.db.base import AsyncSessionLocal
from app.crud.user import get_user
from app.crud import server as crud_server
from app.core.security import decode_access_token
import uuid
import json

router = APIRouter()


@router.websocket("/ws/metrics/{server_id}")
async def metrics_websocket(
    websocket: WebSocket,
    server_id: str,
):
    """
    WebSocket endpoint for frontend clients to receive real-time metrics.
    Authentication via JWT token in initial message (more secure than URL).
    """
    await websocket.accept()
    
    # Get token from initial message (more secure than URL)
    try:
        initial_msg = await websocket.receive_text()
        data = json.loads(initial_msg)
        if data.get("type") != "auth" or not data.get("token"):
            await websocket.close(code=1008, reason="Authentication required: send {'type': 'auth', 'token': '...'} as first message")
            return
        token = data["token"]
    except Exception as e:
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
        return
    
    # Verify token and get user
    try:
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Verify user exists and owns the server
        async with AsyncSessionLocal() as db:
            user = await get_user(db, uuid.UUID(user_id))
            if not user:
                await websocket.close(code=1008, reason="User not found")
                return
            
            # Verify server ownership
            try:
                server_uuid = uuid.UUID(server_id)
                server = await crud_server.get_server(db, server_uuid, user_id=user.id)
                if not server:
                    await websocket.close(code=1008, reason="Server not found or access denied")
                    return
            except ValueError:
                await websocket.close(code=1008, reason="Invalid server ID")
                return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
        return
    
    # Send authentication success
    await websocket.send_json({"type": "auth_success", "message": "Authenticated successfully"})
    
    # Connect to WebSocket manager
    await ws_manager.connect(websocket, server_id)
    
    try:
        # Keep connection alive and wait for disconnect
        while True:
            # Just keep the connection alive - metrics are pushed by ws_manager
            data = await websocket.receive_text()
            # Echo ping/pong for heartbeat
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, server_id)


@router.websocket("/ws/logs/{server_id}")
async def logs_websocket(
    websocket: WebSocket,
    server_id: str,
):
    """
    WebSocket endpoint for frontend clients to receive real-time logs.
    Authentication via JWT token in initial message (more secure than URL).
    """
    await websocket.accept()
    
    # Get token from initial message (more secure than URL)
    try:
        initial_msg = await websocket.receive_text()
        data = json.loads(initial_msg)
        if data.get("type") != "auth" or not data.get("token"):
            await websocket.close(code=1008, reason="Authentication required: send {'type': 'auth', 'token': '...'} as first message")
            return
        token = data["token"]
    except Exception as e:
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
        return
    
    # Verify token and get user
    try:
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Verify user exists and owns the server
        async with AsyncSessionLocal() as db:
            user = await get_user(db, uuid.UUID(user_id))
            if not user:
                await websocket.close(code=1008, reason="User not found")
                return
            
            # Verify server ownership
            try:
                server_uuid = uuid.UUID(server_id)
                server = await crud_server.get_server(db, server_uuid, user_id=user.id)
                if not server:
                    await websocket.close(code=1008, reason="Server not found or access denied")
                    return
            except ValueError:
                await websocket.close(code=1008, reason="Invalid server ID")
                return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
        return
    
    # Send authentication success
    await websocket.send_json({"type": "auth_success", "message": "Authenticated successfully"})
    
    # Connect to WebSocket manager
    await ws_manager.connect(websocket, server_id)
    
    try:
        # Keep connection alive and wait for disconnect
        while True:
            # Just keep the connection alive - logs are pushed by ws_manager
            data = await websocket.receive_text()
            # Echo ping/pong for heartbeat
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, server_id)

