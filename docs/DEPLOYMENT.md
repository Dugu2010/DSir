# DSir — Production Deployment & Operations Guide

This document describes the **actual self-hosted production setup** currently running
on this server. It covers the architecture, every service, how to deploy/rebuild, how
the AI and code sandbox are wired, and troubleshooting.

> For the alternative **cloud** deployment (Render + Vercel), see the git history of this
> file or the original `render.yaml` / `vercel.json` at the repo root.

---

## 1. Architecture at a glance

```
                 ┌─────────────────────────────────────────────┐
  Internet ─────▶│  cloudflared tunnels (systemd)              │
                 │   • dsir.dshost.dpdns.org  → 127.0.0.1:3000 │
                 │   • api.dshost.dpdns.org   → 127.0.0.1:8000 │
                 └───────────────┬──────────────┬──────────────┘
                                 │              │
                                 ▼              ▼
                        ┌────────────────┐   ┌──────────────────────┐
                        │ nginx (:3000)  │   │ Backend (:8000)      │
                        │  • static land-│   │  FastAPI + uvicorn   │
                        │    ing (/)     │   │  (systemd dsir-      │
                        │  • proxies app │   │   backend)           │
                        │    routes +    │   └──────┬───────────────┘
                        │    /pyodide/   │          │
                        └──────┬─────────┘          │
                               │                    ├─ PostgreSQL :5432 (systemd)
                               ▼                    ├─ Redis :6379      (Docker)
                        ┌──────────────────────┐    └─ Ollama :11434    (systemd)
                        │ Frontend (:3001)     │        qwen2.5-coder:7b
                        │ Next.js 15 (prod)    │
                        │ (systemd dsir-       │
                        │  frontend)           │
                        └──────────────────────┘
```

**Ports**

| Port | Service | Managed by |
|------|---------|-----------|
| 80   | nginx (unused for DSir; server default) | systemd |
| 3000 | nginx front-end (landing + app proxy) | systemd |
| 3001 | Next.js production server (`next start`) | systemd `dsir-frontend` |
| 8000 | FastAPI backend (uvicorn) | systemd `dsir-backend` |
| 5432 | PostgreSQL | systemd |
| 6379 | Redis | Docker (`wither-redis`) |
| 11434 | Ollama (local LLM) | systemd `ollama` |

**Domains**

| Domain | Purpose | Tunnel target |
|--------|---------|---------------|
| `https://dsir.dshost.dpdns.org` | Frontend (landing + app) | `localhost:3000` |
| `https://api.dshost.dpdns.org` | Backend API | `localhost:8000` |

The frontend's `NEXT_PUBLIC_API_URL` points at `https://api.dshost.dpdns.org`, so the
browser calls the API domain directly (CORS is configured for both domains).

---

## 2. Directory layout

```
DSir/
├── backend/                 # FastAPI application
│   ├── app/                 #   source (api/, models/, services/, tasks/, utils/)
│   ├── migrations/          #   Alembic migrations
│   ├── .venv/               #   Python virtualenv
│   └── .env                 #   secrets + config (git-ignored)
├── frontend/                # Next.js 15 application
│   ├── src/                 #   app pages, components, lib/
│   ├── public/pyodide/      #   self-hosted Pyodide runtime (offline Python sandbox)
│   ├── .env.local           #   NEXT_PUBLIC_API_URL
│   └── .next/               #   production build output
├── landing/                 # static landing page source
├── docs/                    # this guide + ARCHITECTURE + DATABASE_SCHEMA
├── render.yaml              # (alternative) Render deploy config
└── vercel.json              # (alternative) Vercel config
```

---

## 3. Services (systemd)

The backend and frontend run under systemd and auto-start on reboot.

```bash
# status
systemctl status dsir-backend dsir-frontend

# restart
sudo systemctl restart dsir-backend
sudo systemctl restart dsir-frontend

# logs (live)
sudo journalctl -u dsir-backend -f
sudo journalctl -u dsir-frontend -f
```

**Unit files** (installed in `/etc/systemd/system/`):

- `dsir-backend.service` — runs
  `/data/home/sam/DSir/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  from `/data/home/sam/DSir/backend` (so it reads `.env`).
- `dsir-frontend.service` — runs
  `/data/home/sam/DSir/frontend/node_modules/.bin/next start -p 3001`
  from `/data/home/sam/DSir/frontend`.

Other services already managed by systemd: `postgresql`, `nginx`, `cloudflared`, `ollama`.
Redis runs as a Docker container (`wither-redis`, `redis:7-alpine`, bound to `127.0.0.1:6379`).

---

## 4. Deploying / rebuilding the frontend

The frontend runs a **production build** (`next build` + `next start`), not the dev server.

```bash
cd /data/home/sam/DSir/frontend

# 1. Stop the running server (it holds the .next directory)
sudo systemctl stop dsir-frontend

# 2. Build (also type-checks + lints)
npm run build

# 3. Start again
sudo systemctl start dsir-frontend
```

> `NEXT_PUBLIC_API_URL` is **inlined at build time**, so if you change it in
> `.env.local`, you must rebuild.

---

## 5. Backend changes / migrations

```bash
cd /data/home/sam/DSir/backend

# apply migrations
.venv/bin/alembic upgrade head

# create a new migration after editing models
.venv/bin/alembic revision --autogenerate -m "description"

# seed demo data (courses, users, exercises)
.venv/bin/python -m app.seed
.venv/bin/python -m app.seed_learning

# restart after backend code changes
sudo systemctl restart dsir-backend

# run tests
.venv/bin/python -m pytest -q
```

---

## 6. AI provider (course generation + tutor)

AI runs **locally** via Ollama — no API keys, no usage limits, fully offline.

**Current model:** `qwen2.5-coder:7b` (pulled with `ollama pull qwen2.5-coder:7b`).

**Backend config** (in `backend/.env`):

```env
AI_DEFAULT_PROVIDER=openai
AI_DEFAULT_MODEL=qwen2.5-coder:7b
AI_OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama            # ignored by Ollama; any non-empty value works
```

**Switching models:**

```bash
ollama pull qwen2.5-coder:14b        # larger/better, ~9 GB
# then set AI_DEFAULT_MODEL=qwen2.5-coder:14b in backend/.env and:
sudo systemctl restart dsir-backend
```

**Switching back to Cloudflare Workers AI** (free tier, ~10k neurons/day):

```env
AI_DEFAULT_PROVIDER=openai
AI_DEFAULT_MODEL=@cf/meta/llama-3.3-70b-instruct-fp8-fast
AI_OPENAI_BASE_URL=https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1
OPENAI_API_KEY=<cloudflare-api-token>
```

A backup of the previous Cloudflare config is kept at `backend/.env.bak.cloudflare`.

---

## 7. Code sandbox (offline Pyodide)

The in-browser Python sandbox is **self-hosted** — it does not hit a CDN.

- Runtime files live in `frontend/public/pyodide/` (`pyodide.js`, `pyodide.asm.js`,
  `pyodide.asm.wasm`, `python_stdlib.zip`, `pyodide-lock.json`).
- `frontend/src/components/Sandbox.tsx` loads them from `/pyodide/`.
- nginx proxies `/pyodide/` → `:3001` (see `/etc/nginx/conf.d/dsir-landing.conf`) with
  a 1-day cache header.

Supported languages: **Python** (Pyodide/WebAssembly), **JavaScript**, **HTML**.
Only the Python **standard library** is bundled — third-party packages (numpy etc.)
are not available in the sandbox.

---

## 8. nginx (landing + app routing)

Config: `/etc/nginx/conf.d/dsir-landing.conf`

- `location /` serves the **static landing page** from `/var/www/dsir-landing`
  (SPA fallback to `index.html`).
- Specific app routes (`/login`, `/dashboard`, `/courses`, `/practice`, `/revision`,
  `/profile`, `/settings`, `/achievements`, `/notifications`, `/bookmarks`, `/ai`,
  `/admin`, `/_next`, `/pyodide/`) are proxied to Next.js on `:3001`.
- **Important:** if you add a new top-level app route, add a matching nginx
  `location` block and `sudo nginx -t && sudo nginx -s reload`.

```bash
sudo nginx -t            # validate
sudo nginx -s reload     # apply
```

---

## 9. Demo accounts

| Role | Email | Password |
|------|-------|----------|
| Student | `demo@dsir.dev` | `Demo@123!` |
| Superadmin | `admin@dsir.dev` | `Admin@123!` |

---

## 10. Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| Site returns 502 through the tunnel | `dsir-frontend` or `dsir-backend` down → `systemctl status dsir-backend dsir-frontend`, restart as needed |
| `/pyodide/*` returns HTML (landing page) | nginx missing the `/pyodide/` proxy block → add it and reload nginx (§8) |
| AI import returns "No AI provider configured" | backend `.env` missing a key or Ollama down → check `ollama list` and `AI_OPENAI_BASE_URL` |
| AI generation returns invalid JSON | model too small / over-long response → the parser salvages truncated JSON; try `qwen2.5-coder:14b` |
| Frontend change doesn't show up | forgot to rebuild → §4 (`npm run build` + restart) |
| Login works locally but not publicly | check `CORS_ORIGINS` includes both tunnel domains, and `NEXT_PUBLIC_API_URL` |
| Port already in use | `ss -tlnp \| grep :<port>` to find the PID |

---

## 11. Quick reference — useful commands

```bash
# Full stack status
systemctl status dsir-backend dsir-frontend nginx cloudflared ollama postgresql

# Health checks
curl -s localhost:8000/api/health
curl -s https://api.dshost.dpdns.org/api/health

# Backend logs
sudo journalctl -u dsir-backend -f
# Frontend logs
sudo journalctl -u dsir-frontend -f

# Rebuild + redeploy frontend
cd /data/home/sam/DSir/frontend && sudo systemctl stop dsir-frontend \
  && npm run build && sudo systemctl start dsir-frontend

# Backend tests + typecheck + lint
cd /data/home/sam/DSir/backend && .venv/bin/python -m pytest -q
cd /data/home/sam/DSir/frontend && npx tsc --noEmit && npx next lint
```
