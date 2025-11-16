from fastapi import APIRouter
from app.api.v1 import auth, servers, metrics, logs, docker, commands, alerts, api_keys, agents, ws

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(servers.router, prefix="/servers", tags=["servers"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
api_router.include_router(docker.router, prefix="/docker", tags=["docker"])
api_router.include_router(commands.router, prefix="/commands", tags=["commands"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(ws.router, prefix="", tags=["websocket"])

