# System Architecture

Detailed system architecture documentation for ChatOps.

## Component Overview

### Frontend Architecture

```
┌─────────────────────────────────────────┐
│         React Application               │
├─────────────────────────────────────────┤
│  Pages                                  │
│  ├── Login/Register                     │
│  ├── Servers List                       │
│  ├── Server Detail                      │
│  ├── Alerts                             │
│  └── Settings                           │
├─────────────────────────────────────────┤
│  Components                             │
│  ├── Charts (Recharts)                  │
│  ├── Forms (Shadcn UI)                  │
│  ├── Terminal                           │
│  └── Layout Components                  │
├─────────────────────────────────────────┤
│  State Management                       │
│  ├── Zustand (Auth, Servers)            │
│  └── TanStack Query (Server State)      │
├─────────────────────────────────────────┤
│  API Layer                              │
│  ├── REST Client (Axios)                │
│  └── WebSocket Client                   │
└─────────────────────────────────────────┘
```

### Backend Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│  API Routes (v1)                        │
│  ├── /auth/*                            │
│  ├── /servers/*                         │
│  ├── /metrics/*                         │
│  ├── /docker/*                          │
│  ├── /commands/*                        │
│  ├── /alerts/*                          │
│  ├── /api-keys/*                        │
│  ├── /agents/ws                         │
│  └── /ws/*                              │
├─────────────────────────────────────────┤
│  Services                               │
│  ├── AgentManager                       │
│  ├── WSManager                          │
│  ├── AlertService                       │
│  ├── AuthService                        │
│  └── AuditService                       │
├─────────────────────────────────────────┤
│  CRUD Layer                             │
│  ├── User CRUD                          │
│  ├── Server CRUD                        │
│  ├── Metric CRUD                        │
│  └── ...                                │
├─────────────────────────────────────────┤
│  Database Layer                         │
│  └── SQLAlchemy Async                   │
└─────────────────────────────────────────┘
```

### Agent Architecture

```
┌─────────────────────────────────────────┐
│         Go Agent                        │
├─────────────────────────────────────────┤
│  Components                             │
│  ├── Metrics Collector                  │
│  │   ├── CPU                            │
│  │   ├── Memory                         │
│  │   ├── Disk                           │
│  │   └── Network                        │
│  ├── Docker Client                      │
│  ├── WebSocket Client                   │
│  └── Command Executor                   │
├─────────────────────────────────────────┤
│  Communication                         │
│  ├── WebSocket Connection               │
│  ├── Authentication (API Key)           │
│  └── Message Protocol                   │
└─────────────────────────────────────────┘
```

## Service Layer Details

### AgentManager

**Purpose**: Manages agent WebSocket connections

**Responsibilities**:
- Register/unregister agent connections
- Route commands to agents
- Handle command responses
- Track agent status

**Key Methods**:
- `register_agent(server_id, websocket)`
- `unregister_agent(server_id)`
- `send_command(server_id, command)`
- `get_agent_connection(server_id)`

### WSManager

**Purpose**: Manages frontend WebSocket connections

**Responsibilities**:
- Register frontend clients
- Broadcast metrics to subscribers
- Broadcast logs to subscribers
- Handle client disconnections

**Key Methods**:
- `connect(websocket, server_id, client_type)`
- `disconnect(websocket, server_id)`
- `broadcast_metrics(server_id, metrics)`
- `broadcast_logs(server_id, logs)`

### AlertService

**Purpose**: Manages alert threshold checking

**Responsibilities**:
- Evaluate metrics against thresholds
- Create alerts when thresholds are exceeded
- Resolve alerts when conditions normalize
- Manage alert lifecycle

**Key Methods**:
- `check_metrics_against_thresholds(server_id, metrics)`
- `create_alert(threshold, metric_value)`
- `resolve_alert(alert_id)`

### AuthService

**Purpose**: Handles authentication and authorization

**Responsibilities**:
- JWT token generation
- Token validation
- API key verification
- Password hashing

**Key Methods**:
- `create_access_token(user_id)`
- `verify_token(token)`
- `hash_password(password)`
- `verify_password(plain, hashed)`

## Database Schema

### Core Tables

- **users**: User accounts and authentication
- **servers**: Server definitions
- **api_keys**: Agent authentication keys
- **metrics**: Time-series metrics data
- **alerts**: Alert instances
- **alert_thresholds**: Alert configurations
- **log_entries**: System and application logs
- **command_history**: Executed commands
- **connection_events**: Agent connection/disconnection events
- **audit_logs**: User action audit trail

### Relationships

```
users ──┬── servers (owner)
        ├── api_keys (creator)
        └── audit_logs (actor)

servers ──┬── api_keys
          ├── metrics
          ├── alerts
          ├── alert_thresholds
          ├── log_entries
          ├── command_history
          └── connection_events
```

## Communication Protocols

### Agent → API

**WebSocket Endpoint**: `/api/v1/agents/ws`

**Authentication**: API key in initial message

**Message Types**:
- `auth`: Initial authentication
- `metrics`: System metrics data
- `command_response`: Command execution result
- `docker_response`: Docker operation result

### API → Agent

**Message Types**:
- `auth_success`: Authentication confirmation
- `command`: Command execution request
- `docker_command`: Docker operation request

### Frontend → API

**REST Endpoints**: Standard HTTP methods

**WebSocket Endpoints**:
- `/api/v1/ws/metrics/{server_id}`: Real-time metrics
- `/api/v1/ws/logs/{server_id}`: Real-time logs

**Authentication**: JWT token in initial message

## Security Architecture

### Authentication Flow

```
User Login
    ↓
JWT Token Generated
    ↓
Token Stored (Frontend)
    ↓
Token Sent with Requests
    ↓
API Validates Token
    ↓
Request Processed
```

### API Key Flow

```
API Key Generated
    ↓
Key Stored (Database)
    ↓
Agent Connects with Key
    ↓
API Validates Key
    ↓
Agent Authenticated
```

## Performance Considerations

### Current Optimizations

- Async database operations
- WebSocket for real-time updates
- Connection pooling
- Efficient metrics storage

### Future Optimizations

- Redis caching layer
- Kafka for event streaming
- Database read replicas
- CDN for static assets

## Next Steps

- [Data Flow Diagrams](data-flow.md)
- [Future Architecture](future-architecture.md)

