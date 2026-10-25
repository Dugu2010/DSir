# DSir — AI-Powered Programming Education Platform

A full-stack learning platform with interactive lessons, a real in-browser code sandbox,
AI course generation from any handbook/PDF, spaced-repetition flashcards, quizzes,
projects, discussions, leaderboards, achievements, and certificates.

## Stack

- **Backend** — FastAPI + SQLAlchemy (async) + PostgreSQL + Redis, Alembic migrations
- **Frontend** — Next.js 15 (App Router, TypeScript, Tailwind)
- **AI** — local Ollama (`qwen2.5-coder:7b`), multi-provider fallback (Cloudflare/Gemini/OpenAI/Anthropic)
- **Code sandbox** — Pyodide (Python in WebAssembly, loaded from pinned jsDelivr assets) + isolated JS/HTML iframes; optional server-side grading in a resource-limited child process
- **Deploy** — self-hosted (systemd + nginx + cloudflared tunnels), alt. Render/Vercel configs included

## Documentation

| Doc | What it covers |
|-----|----------------|
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | **Production deployment & operations** — services, systemd, nginx, cloudflared, AI setup, sandbox, troubleshooting |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture |
| [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) | Database schema reference |
| [`docs/QA_REPORT.md`](docs/QA_REPORT.md) | Curriculum content, platform fixes, and verification evidence |
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
python -m app.seed_curriculum   # 20 modules, 40 lessons, 45 exercises, 20 assessments
uvicorn app.main:app --reload --port 8000

# Frontend
cd ../frontend
npm install
cp .env.example .env.local    # set NEXT_PUBLIC_API_URL
npm run dev
```

## Python curriculum

The featured course, **Python Programming: Zero to Job-Ready**, is authored for DSir
and seeded idempotently by `python -m app.seed_curriculum`. It contains 20 modules,
40 substantive lessons, 45 coding/debugging exercises, 20 module assessments
(80 questions), and 12 documented projects (including a capstone). Every exercise's
reference solution is checked by the test suite. Re-running the seeder updates
authored content by stable slugs and never deletes progress, submissions, or accounts.
Its sequence is informed by MIT OCW 6.100L, the official Python Tutorial and
documentation, python.org's beginner resources, and CodeWithHarry's Python handbook;
all lesson prose and exercises are original DSir material.

## Production

The production setup runs `next build` + `next start` under systemd behind nginx,
served publicly through cloudflared tunnels. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
for the full operations guide.

## Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Student | `demo@dsir.dev` | `Demo@123!` |
| Superadmin | `admin@dsir.dev` | `Admin@123!` |
