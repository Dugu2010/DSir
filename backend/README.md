# DSir Backend

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Redis 7+

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Seed data
python -m app.seed

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up -d

# Seed database
docker-compose exec api python -m app.seed
```

### API Documentation
When DEBUG=true: http://localhost:8000/api/docs

### Health Checks
- Liveness: `GET /api/health`
- Readiness: `GET /api/health/ready`
