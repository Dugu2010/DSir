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

# Seed base demo data
python -m app.seed

# Seed/refresh the authored Python curriculum (idempotent)
python -m app.seed_curriculum

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up -d

# Apply migrations and seed
# (run from the host; the api container has the application files)
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.seed
docker-compose exec api python -m app.seed_curriculum
```

### API Documentation
When DEBUG=true: http://localhost:8000/api/docs

### Health Checks
- Liveness: `GET /api/health`
- Readiness: `GET /api/health/ready`
