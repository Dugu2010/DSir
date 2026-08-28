# DSir — AI-Powered Programming Education Platform

A full-stack learning platform with interactive lessons, a real in-browser code sandbox,
AI course generation from any handbook/PDF, spaced-repetition flashcards, quizzes,
projects, discussions, leaderboards, achievements, and certificates.

## Stack

- **Backend** — FastAPI + SQLAlchemy (async) + PostgreSQL + Redis, Alembic migrations
- **Frontend** — Next.js 15 (App Router, TypeScript, Tailwind)
- **AI** — local Ollama (`qwen2.5-coder:7b`), multi-provider fallback (Cloudflare/Gemini/OpenAI/Anthropic)
- **Code sandbox** — self-hosted Pyodide (offline Python in WebAssembly) + JS/HTML iframes
- **Deploy** — self-hosted (systemd + nginx + cloudflared tunnels), alt. Render/Vercel configs included

## Documentation

| Doc | What it covers |
|-----|----------------|
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | **Production deployment & operations** — services, systemd, nginx, cloudflared, AI setup, sandbox, troubleshooting |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Database schema reference |
| [`backend/README.md`](backend/README.md) | Backend quick start |
| [`frontend/README.md`](frontend/README.md) | Frontend quick start |

## Quick start (local dev)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in DATABASE_URL, JWT_SECRET_KEY, AI keys
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000

# Frontend
cd ../frontend
npm install
cp .env.example .env.local    # set NEXT_PUBLIC_API_URL
npm run dev
```

## Production

The production setup runs `next build` + `next start` under systemd behind nginx,
served publicly through cloudflared tunnels. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
for the full operations guide.

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Student | `demo@dsir.dev` | `Demo@123!` |
| Superadmin | `admin@dsir.dev` | `Admin@123!` |
