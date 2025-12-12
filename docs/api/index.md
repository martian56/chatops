# API Reference

Complete API documentation for ChatOps REST and WebSocket APIs.

## Base URL

```
https://your-chatops-instance.com/api/v1
```

## Authentication

ChatOps uses two authentication methods:

1. **JWT Tokens**: For user authentication (REST API and frontend WebSockets)
2. **API Keys**: For agent authentication (agent WebSocket connections)

See [Authentication Guide](authentication.md) for details.

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update profile
- `POST /auth/change-password` - Change password
- `POST /auth/logout` - Logout (invalidate refresh token)

### Servers
- `GET /servers` - List all servers
- `POST /servers` - Create server
- `GET /servers/{id}` - Get server details
- `PUT /servers/{id}` - Update server
- `DELETE /servers/{id}` - Delete server

### Metrics
- `GET /metrics/{server_id}` - Get latest metrics
- `GET /metrics/{server_id}/history` - Get metrics history

### Docker
- `GET /docker/{server_id}/containers` - List containers
- `POST /docker/{server_id}/containers/{container_id}/start` - Start container
- `POST /docker/{server_id}/containers/{container_id}/stop` - Stop container
- `POST /docker/{server_id}/containers/{container_id}/restart` - Restart container
- `GET /docker/{server_id}/containers/{container_id}/logs` - Get container logs

### Commands
- `POST /commands/{server_id}` - Execute command

### Alerts
- `GET /alerts` - List alerts
- `GET /alerts/{id}` - Get alert details
- `POST /alerts/{id}/resolve` - Resolve alert
- `GET /alerts/thresholds` - List alert thresholds
- `POST /alerts/thresholds` - Create alert threshold
- `PUT /alerts/thresholds/{id}` - Update alert threshold
- `DELETE /alerts/thresholds/{id}` - Delete alert threshold

### API Keys
- `GET /api-keys/me` - Get my API keys
- `POST /api-keys` - Create API key
- `DELETE /api-keys/{id}` - Revoke API key

### WebSocket
- `WS /agents/ws` - Agent WebSocket endpoint
- `WS /ws/metrics/{server_id}` - Frontend metrics WebSocket
- `WS /ws/logs/{server_id}` - Frontend logs WebSocket

## Interactive Documentation

When running the API server, interactive documentation is available at:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## Response Format

### Success Response

```json
{
  "data": { ... },
  "message": "Success message (optional)"
}
```

### Error Response

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

Rate limiting is not currently implemented but planned for future versions.

## Next Steps

- [Authentication Guide](authentication.md)
- [REST Endpoints](rest-endpoints.md)
- [WebSocket API](websocket-api.md)
- [API Keys](api-keys.md)

