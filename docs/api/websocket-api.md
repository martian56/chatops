# WebSocket API

Real-time communication via WebSocket connections.

## Endpoints

### Agent WebSocket

```
WS /api/v1/agents/ws
```

**Authentication**: API key in initial message

**Purpose**: Agent connection for metrics and commands

### Frontend Metrics WebSocket

```
WS /api/v1/ws/metrics/{server_id}
```

**Authentication**: JWT token in initial message

**Purpose**: Real-time metrics updates for frontend

### Frontend Logs WebSocket

```
WS /api/v1/ws/logs/{server_id}
```

**Authentication**: JWT token in initial message

**Purpose**: Real-time log streaming for frontend

## Agent WebSocket Protocol

### Connection

1. Connect to `/api/v1/agents/ws`
2. Send authentication message:
   ```json
   {
     "type": "auth",
     "api_key": "your-api-key-here"
   }
   ```
3. Receive authentication response:
   ```json
   {
     "type": "auth_success",
     "server_id": "uuid",
     "message": "Connected successfully"
   }
   ```

### Sending Metrics

Send metrics every 5 seconds:

```json
{
  "type": "metrics",
  "server_id": "uuid",
  "cpu_percent": 45.2,
  "memory_percent": 62.5,
  "disk_usage": [...],
  "network": [...],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Receiving Commands

```json
{
  "type": "command",
  "command_id": "uuid",
  "command": "ls -la"
}
```

### Sending Command Response

```json
{
  "type": "command_response",
  "command_id": "uuid",
  "output": "total 100\n...",
  "exit_code": 0,
  "duration_ms": 150
}
```

### Docker Commands

Receive:
```json
{
  "type": "docker_command",
  "command_id": "uuid",
  "action": "start",
  "container_id": "container-id"
}
```

Respond:
```json
{
  "type": "docker_response",
  "command_id": "uuid",
  "success": true,
  "message": "Container started"
}
```

## Frontend WebSocket Protocol

### Metrics WebSocket

1. Connect to `/api/v1/ws/metrics/{server_id}`
2. Send authentication:
   ```json
   {
     "type": "auth",
     "token": "jwt-access-token"
   }
   ```
3. Receive metrics updates:
   ```json
   {
     "type": "metrics",
     "data": {
       "cpu_percent": 45.2,
       "memory_percent": 62.5,
       ...
     }
   }
   ```

### Logs WebSocket

1. Connect to `/api/v1/ws/logs/{server_id}`
2. Send authentication:
   ```json
   {
     "type": "auth",
     "token": "jwt-access-token"
   }
   ```
3. Receive log entries:
   ```json
   {
     "type": "log",
     "data": {
       "level": "INFO",
       "message": "Log message",
       "timestamp": "2024-01-01T00:00:00Z"
     }
   }
   ```

## Message Types

### Agent Messages

- `auth`: Authentication request
- `auth_success`: Authentication confirmation
- `metrics`: Metrics data
- `command`: Command execution request
- `command_response`: Command execution result
- `docker_command`: Docker operation request
- `docker_response`: Docker operation result

### Frontend Messages

- `auth`: Authentication request
- `metrics`: Metrics update
- `log`: Log entry
- `alert`: Alert notification
- `error`: Error message

## Error Handling

### Authentication Failed

```json
{
  "type": "error",
  "message": "Invalid or inactive API key"
}
```

### Invalid Message

```json
{
  "type": "error",
  "message": "Invalid message format"
}
```

## Reconnection

Both agents and frontend clients should implement automatic reconnection:

1. Detect connection loss
2. Wait for exponential backoff
3. Reconnect and re-authenticate
4. Resume normal operation

## Best Practices

1. **Always authenticate first** before sending other messages
2. **Handle reconnections** gracefully
3. **Validate message types** before processing
4. **Implement heartbeat** to detect connection issues
5. **Use TLS/SSL** in production

## Next Steps

- [REST Endpoints](rest-endpoints.md)
- [API Keys](api-keys.md)

