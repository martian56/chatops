# Docker Deployment

Deploy ChatOps using Docker and Docker Compose.

## Quick Start

```bash
# Clone repository
git clone https://github.com/martian56/chatops.git
cd chatops

# Create .env file
cat > api/.env << EOF
DATABASE_URL=postgresql://user:password@db:5432/chatops
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:5173"]
EOF

# Start services
docker compose up -d --build
```

## Services

### API Service

- **Image**: Built from `api/Dockerfile`
- **Port**: 8000
- **Environment**: See `api/.env`
- **Dependencies**: Database service

### Database Service

- **Image**: `postgres:16-alpine`
- **Port**: 5432
- **Volume**: `postgres_data`

## Dockerfile Details

The API Dockerfile:

- Uses Python 3.12-slim base image
- Runs as non-root user (`appuser`)
- Installs dependencies
- Runs Alembic migrations on startup
- Exposes port 8000

## Environment Variables

See `docker-compose.yml` for environment variable configuration.

## Volumes

- `postgres_data`: PostgreSQL data persistence

## Next Steps

- [Production Deployment](production.md)

