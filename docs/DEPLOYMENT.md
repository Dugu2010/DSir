# DSir — Deployment Guide

## Backend Deployment (Render)

### Prerequisites
- Render account
- PostgreSQL database (managed or external)
- Redis instance (optional, for caching)

### Steps

1. **Create a PostgreSQL database on Render**
   - Go to Render Dashboard → New → PostgreSQL
   - Note the Internal Database URL and External Database URL

2. **Create a Web Service**
   - Connect your GitHub repository
   - Set Root Directory to `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

3. **Set Environment Variables**
   ```
   DATABASE_URL=postgresql+asyncpg://...  (from Render PostgreSQL)
   JWT_SECRET_KEY=<generate a strong random string>
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   OPENAI_API_KEY=sk-...                    (optional)
   ANTHROPIC_API_KEY=sk-ant-...             (optional)
   ENVIRONMENT=production
   ```

4. **Run Database Seed**
   - After first deploy, use Render Shell:
   ```bash
   python -m app.seed
   ```

### Health Checks
- Liveness: `GET https://your-backend.onrender.com/api/health`
- Readiness: `GET https://your-backend.onrender.com/api/health/ready`

---

## Frontend Deployment (Vercel)

### Steps

1. **Import Project on Vercel**
   - Connect your GitHub repository
   - Set Root Directory to `frontend`
   - Framework Preset: Next.js

2. **Set Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```

3. **Deploy**
   - Vercel automatically builds and deploys on push

---

## Local Docker Deployment

```bash
# Clone repository
git clone <repo-url>
cd dsir

# Start backend services
cd backend
docker-compose up -d

# Seed database
docker-compose exec api python -m app.seed

# Start frontend
cd ../frontend
npm install
npm run dev
```

---

## Environment Variables Reference

### Backend
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string (asyncpg) |
| `JWT_SECRET_KEY` | Yes | — | Secret key for JWT signing |
| `REDIS_URL` | No | — | Redis connection string |
| `OPENAI_API_KEY` | No | — | OpenAI API key for AI features |
| `ANTHROPIC_API_KEY` | No | — | Anthropic API key for AI features |
| `CORS_ORIGINS` | No | `["http://localhost:3000"]` | Allowed CORS origins (JSON array) |
| `RATE_LIMIT_GLOBAL` | No | `100` | Max requests per window |
| `DEBUG` | No | `false` | Enable debug mode |

### Frontend
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API base URL |

---

## Production Checklist

- [ ] Generate strong `JWT_SECRET_KEY` (min 32 chars, random)
- [ ] Set `DEBUG=false`
- [ ] Configure CORS origins to your actual frontend domain
- [ ] Set up SSL/TLS (Render/Vercel handle this automatically)
- [ ] Configure database backups
- [ ] Set up monitoring (Render metrics, Vercel analytics)
- [ ] Enable rate limiting (already configured, tune values)
- [ ] Rotate API keys regularly
- [ ] Review security headers
- [ ] Run database backups before major updates
