# Deployment Guide

Deployment guides for ChatOps in various environments.

## Deployment Options

1. **Docker Compose**: Quick setup for development and small deployments
2. **Production**: Manual deployment with best practices
3. **Cloud**: Deploy to cloud platforms (AWS, GCP, Azure)

## Quick Start with Docker

```bash
# Clone repository
git clone https://github.com/martian56/chatops.git
cd chatops

# Configure environment
cat > api/.env << EOF
DATABASE_URL=postgresql://user:password@db:5432/chatops
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:5173"]
EOF

# Start services
docker compose up -d --build
```

## Production Deployment

See [Production Deployment Guide](production.md) for:
- Security best practices
- Performance optimization
- Monitoring and logging
- Backup strategies

## Docker Deployment

See [Docker Deployment Guide](docker.md) for:
- Dockerfile details
- Docker Compose configuration
- Container orchestration

## Next Steps

- [Docker Guide](docker.md)
- [Production Guide](production.md)

