# Data Flow

Detailed data flow diagrams and explanations for ChatOps operations.

## Metrics Collection Flow

```
┌─────────┐
│  Agent  │
└────┬────┘
     │ Collects metrics every 5 seconds
     │ (CPU, Memory, Disk, Network)
     ↓
┌─────────────────────┐
│  WebSocket Client   │
│  (Agent)            │
└────┬────────────────┘
     │ Sends metrics via WebSocket
     ↓
┌─────────────────────┐
│  API Endpoint       │
│  /agents/ws         │
└────┬────────────────┘
     │
     ├──→ AgentManager
     │    ├── Register connection
     │    └── Store metrics
     │
     ├──→ Database (PostgreSQL)
     │    └── Store metrics with timestamp
     │
     ├──→ AlertService
     │    ├── Check thresholds
     │    ├── Create alerts if needed
     │    └── Resolve alerts if conditions normalize
     │
     └──→ WSManager
          └── Broadcast to frontend clients
               ↓
          ┌─────────────────────┐
          │  Frontend Clients   │
          │  (WebSocket)        │
          └─────────────────────┘
               ↓
          ┌─────────────────────┐
          │  UI Updates         │
          │  (Charts, Metrics)  │
          └─────────────────────┘
```

## Command Execution Flow

```
┌──────────────┐
│   Frontend   │
│   (User)     │
└──────┬───────┘
       │ User enters command
       ↓
┌─────────────────────┐
│  REST API           │
│  POST /commands/    │
└──────┬──────────────┘
       │
       ├──→ Authentication (JWT)
       ├──→ Authorization (User owns server)
       └──→ Command Service
            │
            ├──→ AgentManager
            │    ├── Find agent connection
            │    └── Send command via WebSocket
            │         ↓
            └──→ Agent
                 │ Receives command
                 ├──→ Execute command
                 ├──→ Capture output
                 └──→ Send response
                      ↓
                 ┌─────────────────────┐
                 │  WebSocket Response │
                 └──────┬──────────────┘
                        ↓
                 ┌─────────────────────┐
                 │  AgentManager       │
                 │  (Receives response)│
                 └──────┬──────────────┘
                        ↓
                 ┌─────────────────────┐
                 │  Database           │
                 │  (Store history)    │
                 └──────┬──────────────┘
                        ↓
                 ┌─────────────────────┐
                 │  REST Response      │
                 │  (Return to User)   │
                 └──────┬──────────────┘
                        ↓
                 ┌─────────────────────┐
                 │  Frontend           │
                 │  (Display output)   │
                 └─────────────────────┘
```

## Docker Operations Flow

```
┌──────────────┐
│   Frontend   │
│   (User)     │
└──────┬───────┘
       │ User clicks container action
       │ (Start, Stop, Restart, etc.)
       ↓
┌─────────────────────┐
│  REST API           │
│  POST /docker/      │
│  /containers/{id}/  │
│  {action}           │
└──────┬──────────────┘
       │
       ├──→ Authentication (JWT)
       ├──→ Authorization (User owns server)
       └──→ Docker Service
            │
            ├──→ AgentManager
            │    ├── Find agent connection
            │    └── Send Docker command via WebSocket
            │         ↓
            └──→ Agent
                 │ Receives Docker command
                 ├──→ Docker Client
                 │    ├── Execute Docker operation
                 │    └── Get container status
                 └──→ Send response
                      ↓
                 ┌─────────────────────┐
                 │  WebSocket Response │
                 └──────┬──────────────┘
                        ↓
                 ┌─────────────────────┐
                 │  REST Response      │
                 │  (Return to User)   │
                 └──────┬──────────────┘
                        ↓
                 ┌─────────────────────┐
                 │  Frontend           │
                 │  (Update UI)        │
                 └─────────────────────┘
```

## Authentication Flow

### User Login

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ POST /auth/login
       │ {username, password}
       ↓
┌─────────────────────┐
│  Auth Service       │
└──────┬──────────────┘
       │
       ├──→ Verify credentials
       ├──→ Generate JWT tokens
       │    ├── Access token (30 min)
       │    └── Refresh token (7 days)
       └──→ Return tokens
            ↓
┌─────────────────────┐
│  Frontend           │
│  (Store tokens)     │
└─────────────────────┘
```

### Agent Authentication

```
┌─────────┐
│  Agent  │
└────┬────┘
     │ Connect to /agents/ws
     │ Send: {"type": "auth", "api_key": "..."}
     ↓
┌─────────────────────┐
│  API Endpoint       │
│  /agents/ws         │
└────┬────────────────┘
     │
     ├──→ Verify API key
     │    ├── Check database
     │    ├── Verify active status
     │    └── Get server_id
     │
     ├──→ Register agent
     │    ├── AgentManager.register_agent()
     │    └── Update server status to ONLINE
     │
     └──→ Send auth_success
          ↓
     ┌─────────────────────┐
     │  Agent              │
     │  (Start sending     │
     │   metrics)          │
     └─────────────────────┘
```

## Alert Evaluation Flow

```
┌─────────────────────┐
│  Metrics Received   │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│  AlertService       │
└──────┬──────────────┘
       │
       ├──→ Fetch thresholds for server
       ├──→ Evaluate each threshold
       │    ├── Compare metric value
       │    ├── Check comparison operator (>, <, =)
       │    └── Check if threshold enabled
       │
       ├──→ If threshold exceeded:
       │    ├── Check if alert already exists
       │    ├── Create new alert if not exists
       │    └── Log alert creation
       │
       └──→ If threshold normalized:
            ├── Find active alert
            ├── Resolve alert
            └── Log alert resolution
                 ↓
            ┌─────────────────────┐
            │  Database           │
            │  (Store alert)      │
            └─────────────────────┘
                 ↓
            ┌─────────────────────┐
            │  Frontend           │
            │  (Display alert)    │
            └─────────────────────┘
```

## Real-time Updates Flow

```
┌─────────┐
│  Agent  │
└────┬────┘
     │ Sends metrics
     ↓
┌─────────────────────┐
│  API (AgentManager) │
└──────┬──────────────┘
       │
       ├──→ Store in database
       └──→ WSManager.broadcast_metrics()
            │
            ├──→ Get all subscribers for server_id
            ├──→ For each WebSocket connection:
            │    └──→ Send metrics JSON
            │         ↓
            └──→ Frontend Clients
                 │ Receive metrics
                 ├──→ Update TanStack Query cache
                 ├──→ Update Zustand store
                 └──→ Re-render UI components
                      ├── Charts update
                      ├── Metrics display updates
                      └── Status indicators update
```

## Error Handling Flow

```
┌─────────────────────┐
│  Operation Fails    │
└──────┬──────────────┘
       │
       ├──→ Try/Catch block
       ├──→ Log error
       │    ├── Error message
       │    ├── Stack trace
       │    └── Context (user, server, etc.)
       │
       ├──→ Return appropriate HTTP status
       │    ├── 400: Bad Request
       │    ├── 401: Unauthorized
       │    ├── 403: Forbidden
       │    ├── 404: Not Found
       │    └── 500: Internal Server Error
       │
       └──→ Frontend handles error
            ├── Display error message
            └── Log for debugging
```

## Next Steps

- [System Architecture](system-architecture.md)
- [Future Architecture](future-architecture.md)

