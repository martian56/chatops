# Architecture Overview

ChatOps follows a three-tier architecture designed for scalability, reliability, and real-time performance.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React Web Frontend (Vite + TypeScript)              │   │
│  │  - TanStack Query (Data Fetching)                    │   │
│  │  - Zustand (State Management)                        │   │
│  │  - WebSocket Client (Real-time Updates)              │   │
│  │  - Tailwind CSS + Shadcn UI                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend (Python)                            │   │ 
│  │  ├── REST API Endpoints                              │   │
│  │  ├── WebSocket Endpoints                             │   │
│  │  ├── Agent Manager (WebSocket Connections)           │   │
│  │  ├── WS Manager (Client Connections)                 │   │
│  │  ├── Alert Service (Threshold Checking)              │   │
│  │  └── Auth Service (JWT + API Keys)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ SQLAlchemy Async
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database (Async via asyncpg)             │   │
│  │  ├── Users, Servers, API Keys                        │   │
│  │  ├── Metrics (Time-series data)                      │   │
│  │  ├── Alerts, Logs, Audit Logs                        │   │
│  │  └── Command History, Connection Events              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Go Agent (Lightweight Binary)                       │   │
│  │  ├── Metrics Collector (CPU, Memory, Disk, Network)  │   │
│  │  ├── Docker Client (Container Management)            │   │
│  │  ├── WebSocket Client (Bidirectional)                │   │
│  │  └── Command Executor                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Web Frontend

**Location**: `web/`

- React 18 with TypeScript
- Vite for fast development and builds
- TanStack Query for server state management
- Zustand for client state
- WebSocket API for real-time updates
- Tailwind CSS + Shadcn UI for styling

### 2. API Backend

**Location**: `api/`

- FastAPI (async Python web framework)
- SQLAlchemy async ORM
- PostgreSQL with asyncpg driver
- WebSocket support for real-time communication
- JWT authentication
- Alembic for database migrations

### 3. Agent

**Location**: `agent/`

- Go 1.24+ binary
- Lightweight and efficient
- Docker client integration
- WebSocket client for bidirectional communication
- System metrics collection

### 4. Database

- PostgreSQL 16+
- Async operations via asyncpg
- Time-series metrics storage
- Full audit logging

## Data Flow

### Metrics Collection

```
Agent → WebSocket → API Agent Endpoint → AgentManager
                                              ↓
                                    Store in PostgreSQL
                                              ↓
                                    Check Alert Thresholds
                                              ↓
                                    Broadcast to Frontend (WSManager)
                                              ↓
                                    Frontend Updates UI
```

### Command Execution

```
Frontend → REST API → AgentManager → Agent WebSocket
                                              ↓
                                    Agent Executes Command
                                              ↓
                                    Response via WebSocket
                                              ↓
                                    AgentManager → Response Queue
                                              ↓
                                    REST API Response → Frontend
```

## Key Design Decisions

### Real-time Communication

- **WebSockets** for bidirectional communication
- Separate endpoints for agents and frontend clients
- Message-based protocol for commands and responses

### Authentication

- **JWT tokens** for user authentication
- **API keys** for agent authentication
- Refresh token mechanism for session management

### Database

- **PostgreSQL** for relational data
- Async operations for better performance
- Time-series data stored with timestamps

### Scalability

- Stateless API design
- In-memory connection management (current)
- Future: Redis for distributed state

## Current Limitations

1. **In-Memory State**: Agent connections stored in memory
2. **Single Instance**: No horizontal scaling support
3. **No Message Queue**: Direct WebSocket communication
4. **Synchronous Alert Checking**: Alert checks during metric processing

## Future Architecture

See [Future Architecture](future-architecture.md) for planned improvements including:
- Kafka for event streaming
- Redis for distributed caching
- Microservices architecture
- TimescaleDB for metrics

## Next Steps

- [System Architecture Details](system-architecture.md)
- [Data Flow Diagrams](data-flow.md)
- [Future Architecture Plans](future-architecture.md)

