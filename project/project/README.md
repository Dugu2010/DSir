# DSir

DSir is an AI-powered programming education platform designed to take learners from complete beginners to industry-ready software developers.

## Architecture

- **Frontend:** Next.js, React, TypeScript
- **Backend:** FastAPI, Python
- **Database:** PostgreSQL with pgvector
- **Cache:** Redis
- **Storage:** S3-compatible
- **Deployment:** Docker

## Getting Started

```bash
# Copy environment variables
cp .env.example .env

# Start services with Docker Compose
docker-compose up --build

# Run migrations
docker-compose exec api alembic upgrade head

# Open the app
# Web: http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Documentation

Design documents are in the `docs/` directory.

## Development

See `docs/16-development-roadmap.md` for the full development plan.
