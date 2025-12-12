# Development Setup

Set up your development environment for ChatOps.

## Prerequisites

- Python 3.12+
- Node.js 18+
- Go 1.24+
- PostgreSQL 16+
- Docker (optional)

## Backend Setup

```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

## Frontend Setup

```bash
cd web
npm install

# Create .env file
cp .env.example .env
# Edit .env with your API URL

# Start dev server
npm run dev
```

## Agent Setup

```bash
cd agent
go build -o chatops-agent ./main.go
./chatops-agent -api-key YOUR_KEY -api-url http://localhost:8000
```

## Running Tests

### Backend

```bash
cd api
pytest
```

### Frontend

```bash
cd web
npm test
```

## Code Style

- **Python**: PEP 8, use `black` for formatting
- **TypeScript**: ESLint rules
- **Go**: `gofmt`

## Next Steps

- [Testing Guide](testing.md)

