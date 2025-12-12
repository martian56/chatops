# REST API Endpoints

Complete reference for all REST API endpoints.

## Base URL

```
https://your-chatops-instance.com/api/v1
```

## Authentication

Most endpoints require authentication. Include the JWT token in the `Authorization` header:

```
Authorization: Bearer your_access_token
```

## Servers

### List Servers

```http
GET /servers
Authorization: Bearer {token}
```

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "Production Server",
    "host": "192.168.1.100",
    "port": 22,
    "status": "online",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### Create Server

```http
POST /servers
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "New Server",
  "host": "192.168.1.101",
  "port": 22
}
```

### Get Server

```http
GET /servers/{id}
Authorization: Bearer {token}
```

### Update Server

```http
PUT /servers/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name"
}
```

### Delete Server

```http
DELETE /servers/{id}
Authorization: Bearer {token}
```

## Metrics

### Get Latest Metrics

```http
GET /metrics/{server_id}
Authorization: Bearer {token}
```

**Response**:
```json
{
  "server_id": "uuid",
  "cpu_percent": 45.2,
  "memory_percent": 62.5,
  "disk_usage": [
    {
      "path": "/",
      "total": 1000000000,
      "used": 500000000,
      "free": 500000000,
      "percent": 50.0
    }
  ],
  "network": [
    {
      "interface": "eth0",
      "bytes_sent": 1000000,
      "bytes_recv": 2000000
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Get Metrics History

```http
GET /metrics/{server_id}/history?start=2024-01-01T00:00:00Z&end=2024-01-01T23:59:59Z
Authorization: Bearer {token}
```

## Docker

### List Containers

```http
GET /docker/{server_id}/containers
Authorization: Bearer {token}
```

### Start Container

```http
POST /docker/{server_id}/containers/{container_id}/start
Authorization: Bearer {token}
```

### Stop Container

```http
POST /docker/{server_id}/containers/{container_id}/stop?timeout=10
Authorization: Bearer {token}
```

### Restart Container

```http
POST /docker/{server_id}/containers/{container_id}/restart?timeout=10
Authorization: Bearer {token}
```

### Get Container Logs

```http
GET /docker/{server_id}/containers/{container_id}/logs?tail=100
Authorization: Bearer {token}
```

## Commands

### Execute Command

```http
POST /commands/{server_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "command": "ls -la"
}
```

**Response**:
```json
{
  "command_id": "uuid",
  "command": "ls -la",
  "output": "total 100\n...",
  "exit_code": 0,
  "duration_ms": 150
}
```

## Alerts

### List Alerts

```http
GET /alerts?status=active&server_id={uuid}
Authorization: Bearer {token}
```

### Resolve Alert

```http
POST /alerts/{id}/resolve
Authorization: Bearer {token}
```

### List Thresholds

```http
GET /alerts/thresholds?server_id={uuid}
Authorization: Bearer {token}
```

### Create Threshold

```http
POST /alerts/thresholds
Authorization: Bearer {token}
Content-Type: application/json

{
  "server_id": "uuid",
  "metric_type": "cpu",
  "threshold_value": 80.0,
  "comparison": "gt",
  "enabled": true
}
```

## API Keys

### List My API Keys

```http
GET /api-keys/me
Authorization: Bearer {token}
```

### Create API Key

```http
POST /api-keys
Authorization: Bearer {token}
Content-Type: application/json

{
  "server_id": "uuid",
  "name": "Production Agent"
}
```

**Response**:
```json
{
  "id": "uuid",
  "name": "Production Agent",
  "server_id": "uuid",
  "key": "chatops_xxxxxxxxxxxx",  // Only shown once!
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Revoke API Key

```http
DELETE /api-keys/{id}
Authorization: Bearer {token}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Interactive Documentation

For interactive API documentation, visit:
- `/docs` - Swagger UI
- `/redoc` - ReDoc

## Next Steps

- [WebSocket API](websocket-api.md)
- [API Keys](api-keys.md)
- [Authentication](authentication.md)

