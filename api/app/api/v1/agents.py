from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.db.base import AsyncSessionLocal
from app.crud.api_key import verify_and_get_api_key
from app.crud import server as server_crud
from app.crud import metric as crud_metric
from app.crud import connection_event as crud_connection_event
from app.services.ws_manager import ws_manager
from app.services.agent_manager import agent_manager
from app.services.alert_service import check_metrics_against_thresholds
from app.api.v1.metrics import metrics_cache
from app.models.server import ServerStatus
from app.models.connection_event import ConnectionEventType
import json
from datetime import datetime
import uuid

router = APIRouter()


@router.websocket("/ws")
async def agent_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for agents to connect and send metrics.
    Authentication via API key in initial message (more secure than URL).
    """
    await websocket.accept()
    
    # Get API key from initial message (more secure than URL)
    try:
        initial_msg = await websocket.receive_text()
        data = json.loads(initial_msg)
        if data.get("type") != "auth" or not data.get("api_key"):
            await websocket.close(code=1008, reason="Authentication required: send {'type': 'auth', 'api_key': '...'} as first message")
            return
        api_key = data["api_key"]
    except Exception as e:
        await websocket.close(code=1008, reason=f"Authentication failed: {str(e)}")
        return
    
    # Verify API key
    server_id = None
    async with AsyncSessionLocal() as db:
        try:
            api_key_obj = await verify_and_get_api_key(db, api_key)
            if not api_key_obj or not api_key_obj.is_active:
                await websocket.close(code=1008, reason="Invalid or inactive API key")
                return
            
            server_id = str(api_key_obj.server_id)
            
            # Register agent connection
            agent_manager.register_agent(server_id, websocket)
            
            # Update server status to ONLINE and log connection event
            try:
                async with AsyncSessionLocal() as status_db:
                    await server_crud.update_server_status(
                        status_db,
                        uuid.UUID(server_id),
                        ServerStatus.ONLINE,
                        update_last_seen=True
                    )
                    # Log connection event
                    await crud_connection_event.create_connection_event(
                        status_db,
                        server_id=uuid.UUID(server_id),
                        event_type=ConnectionEventType.CONNECTED,
                    )
            except Exception as e:
                print(f"Error updating server status to ONLINE or logging connection: {e}")
            
            # Send authentication success
            await websocket.send_json({
                "type": "auth_success",
                "server_id": server_id,
                "message": "Connected successfully"
            })
            
            # Process messages from agent
            # We need to handle both metrics and command responses
            # For now, we'll process metrics synchronously and handle command responses separately
            try:
                while True:
                    # Receive message from agent
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Check if this is a command response (has request_id)
                    if message.get("request_id"):
                        # This is a command response - put it in the response queue
                        agent_manager.put_response(message.get("request_id"), message)
                        continue
                    
                    if message.get("type") == "metrics":
                        # Process metrics
                        metrics_data = message.get("data", {})
                        
                        # Parse timestamp
                        timestamp_str = metrics_data.get("timestamp")
                        if isinstance(timestamp_str, str):
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except:
                                timestamp = datetime.utcnow()
                        else:
                            timestamp = datetime.utcnow()
                        
                        # Store in cache
                        metrics_dict = {
                            "server_id": server_id,
                            "timestamp": timestamp.isoformat(),
                            "cpu": metrics_data.get("cpu", {}),
                            "memory": metrics_data.get("memory", {}),
                            "disk": metrics_data.get("disk", {}),
                            "network": metrics_data.get("network", {}),
                            "containers": metrics_data.get("containers", []),
                            "processes": metrics_data.get("processes", []),
                        }
                        
                        metrics_cache[server_id] = metrics_dict
                        
                        # Persist metrics to database and update server last_seen
                        try:
                            async with AsyncSessionLocal() as metrics_db:
                                # Persist metrics
                                await crud_metric.create_metric(
                                    metrics_db,
                                    server_id=uuid.UUID(server_id),
                                    metrics_data=metrics_dict,
                                )
                                # Update server last_seen timestamp
                                await server_crud.update_server_status(
                                    metrics_db,
                                    uuid.UUID(server_id),
                                    ServerStatus.ONLINE,
                                    update_last_seen=True
                                )
                        except Exception as e:
                            print(f"Error persisting metrics or updating server last_seen: {e}")
                        
                        # Check metrics against alert thresholds and create alerts if needed
                        try:
                            async with AsyncSessionLocal() as alert_db:
                                await check_metrics_against_thresholds(
                                    alert_db,
                                    uuid.UUID(server_id),
                                    metrics_dict,
                                )
                                # Note: create_alert already commits, but we ensure any other changes are committed
                                await alert_db.commit()
                        except Exception as e:
                            # Log error but don't fail the metrics processing
                            print(f"Error checking alert thresholds: {e}")
                            import traceback
                            traceback.print_exc()
                        
                        # Broadcast to frontend clients
                        await ws_manager.send_metrics(server_id, metrics_dict)
                        
                        # Send acknowledgment
                        await websocket.send_json({
                            "type": "metrics_received",
                            "status": "ok"
                        })
                    
                    elif message.get("type") == "ping":
                        # Heartbeat
                        await websocket.send_json({"type": "pong"})
                    
            except WebSocketDisconnect:
                if server_id:
                    agent_manager.unregister_agent(server_id)
                    # Update server status to OFFLINE and log disconnection event
                    try:
                        async with AsyncSessionLocal() as disconnect_db:
                            await server_crud.update_server_status(
                                disconnect_db,
                                uuid.UUID(server_id),
                                ServerStatus.OFFLINE,
                                update_last_seen=False
                            )
                            # Log disconnection event
                            await crud_connection_event.create_connection_event(
                                disconnect_db,
                                server_id=uuid.UUID(server_id),
                                event_type=ConnectionEventType.DISCONNECTED,
                            )
                    except Exception as e:
                        print(f"Error updating server status to OFFLINE or logging disconnection: {e}")
                pass
            except Exception as e:
                if server_id:
                    agent_manager.unregister_agent(server_id)
                    # Update server status to OFFLINE and log error event
                    try:
                        async with AsyncSessionLocal() as error_db:
                            await server_crud.update_server_status(
                                error_db,
                                uuid.UUID(server_id),
                                ServerStatus.OFFLINE,
                                update_last_seen=False
                            )
                            # Log error event
                            await crud_connection_event.create_connection_event(
                                error_db,
                                server_id=uuid.UUID(server_id),
                                event_type=ConnectionEventType.ERROR,
                                error_message=str(e),
                            )
                    except Exception as disconnect_error:
                        print(f"Error updating server status to OFFLINE or logging error: {disconnect_error}")
                await websocket.close(code=1011, reason=f"Error: {str(e)}")
        except Exception as e:
            await websocket.close(code=1011, reason=f"Database error: {str(e)}")

