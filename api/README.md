# ChatOps API

FastAPI backend for the ChatOps server monitoring platform.

## Features

- RESTful API with automatic OpenAPI documentation
- WebSocket support for real-time metrics and logs
- JWT authentication with refresh tokens
- Comprehensive audit logging
- Alert threshold management
- Docker container control via agents
- Command execution tracking
- Database persistence for metrics, logs, and events

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/chatops
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile
- `POST /api/v1/auth/change-password` - Change password

### Servers
- `GET /api/v1/servers` - List all servers
- `POST /api/v1/servers` - Create server
- `GET /api/v1/servers/{id}` - Get server details
- `PUT /api/v1/servers/{id}` - Update server
- `DELETE /api/v1/servers/{id}` - Delete server

### Metrics
- `GET /api/v1/metrics/{server_id}` - Get server metrics
- `GET /api/v1/metrics/{server_id}/history` - Get metrics history

### Docker
- `GET /api/v1/docker/{server_id}/containers` - List containers
- `POST /api/v1/docker/{server_id}/containers/{id}/start` - Start container
- `POST /api/v1/docker/{server_id}/containers/{id}/stop` - Stop container
- `POST /api/v1/docker/{server_id}/containers/{id}/restart` - Restart container
- `GET /api/v1/docker/{server_id}/containers/{id}/logs` - Get container logs

### Commands
- `POST /api/v1/commands/{server_id}` - Execute command

### Alerts
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/thresholds` - List alert thresholds
- `POST /api/v1/alerts/thresholds` - Create threshold
- `PUT /api/v1/alerts/thresholds/{id}` - Update threshold
- `DELETE /api/v1/alerts/thresholds/{id}` - Delete threshold

### Logs
- `GET /api/v1/logs/{server_id}` - Get server logs

### WebSocket
- `WS /api/v1/ws/metrics/{server_id}` - Real-time metrics stream
- `WS /api/v1/ws/logs/{server_id}` - Real-time logs stream
- `WS /api/v1/agents/ws` - Agent connection endpoint

## Database Models

- **User** - User accounts
- **Server** - Monitored servers
- **Alert** - Active alerts
- **AlertThreshold** - Alert configuration
- **Metric** - Time-series metrics
- **LogEntry** - Application logs
- **CommandHistory** - Terminal command history
- **ConnectionEvent** - Agent connection events
- **AuditLog** - User action audit trail
- **APIKey** - Server API keys

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Code Structure

```
app/
├── api/          # API routes
│   └── v1/       # API version 1
├── core/         # Core configuration
├── crud/         # Database operations
├── db/           # Database setup
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
└── services/     # Business logic
```

## Security

- All endpoints (except auth) require JWT authentication
- Passwords are hashed using bcrypt
- API keys are hashed before storage
- CORS is configured for allowed origins
- SQL injection protection via SQLAlchemy ORM

