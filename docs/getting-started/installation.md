# Installation Guide

Complete installation guide for ChatOps components.

## Overview

ChatOps consists of three main components:

1. **Web Frontend** - React-based user interface
2. **API Backend** - FastAPI server
3. **Agent** - Go binary for server monitoring

## Prerequisites

### For Backend/API

- Python 3.12+
- PostgreSQL 16+
- Docker (optional, for containerized deployment)

### For Frontend

- Node.js 18+
- npm or yarn

### For Agent

- Linux/Unix system
- Docker (optional, for container management features)

## Backend Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
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

# The API will be available at http://localhost:8000
```

### Option 2: Manual Installation

```bash
# Create virtual environment
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost/chatops
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:5173"]
EOF

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Installation

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
EOF

# Development server
npm run dev

# Production build
npm run build
```

## Agent Installation

See the [Agent Installation Guide](../agent/installation.md) for detailed instructions.

## Database Setup

### PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-16

# macOS (Homebrew)
brew install postgresql@16
brew services start postgresql@16

# Create database
sudo -u postgres psql
CREATE DATABASE chatops;
CREATE USER chatops_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatops TO chatops_user;
\q
```

### Run Migrations

```bash
cd api
alembic upgrade head
```

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/chatops

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## Verification

### Backend

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### Frontend

```bash
# Open in browser
open http://localhost:5173
```

## Production Deployment

For production deployment, see the [Production Deployment Guide](../deployment/production.md).

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database and user exist

### Port Conflicts

- Change API port: `--port 8001`
- Change frontend port: Update `vite.config.ts`

### Migration Errors

- Check database connection
- Verify Alembic configuration
- Review migration files

## Next Steps

- [Quick Start Guide](quick-start.md)
- [Production Deployment](../deployment/production.md)
- [Configuration Guide](../agent/configuration.md)

