# DSir — System Architecture

## Overview

DSir is an AI-powered programming education platform delivering a complete learning experience from absolute beginner to job-ready software engineer. The platform combines interactive lessons, a practice engine, AI-driven tutoring, spaced-repetition revision, gamification, and career guidance into a cohesive SaaS product.

---

## Architecture Principles

1. **API-First** — Every feature exposed via versioned REST APIs consumed by the frontend and future clients.
2. **Clean Architecture** — Separation into domain models, services, infrastructure, and presentation layers.
3. **Modular Monolith (Phase 1)** — FastAPI monolith organized by bounded contexts; extractable into microservices later.
4. **Type Safety** — Python with strict mypy, TypeScript with strict mode.
5. **Security by Default** — OWASP compliance, zero-trust sandboxing, principle of least privilege.
6. **Observable** — Structured logging, request tracing, health checks, metrics.
7. **Accessible** — WCAG 2.1 AA minimum; full keyboard navigation; screen-reader support.

---

## System Context

```
┌────────────────────────────────────────────────────────────┐
│                        CLIENTS                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Browser  │  │  Mobile   │  │   PWA    │  │  API     │  │
│  │  (Next.js)│  │  (Future) │  │          │  │  Clients │  │
│  └─────┬─────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘  │
└────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │
    ┌────▼──────────────▼──────────────▼──────────────▼──────┐
    │                   CDN / Vercel Edge                     │
    │      Static Assets, SSR Pages, API Proxying             │
    └────────────────────────┬───────────────────────────────┘
                             │
    ┌────────────────────────▼───────────────────────────────┐
    │                 API Gateway (FastAPI)                    │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
    │  │   Auth   │ │ Rate Lim │ │   CORS   │ │  Audit   │  │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │                Route Handlers                     │  │
    │  │  Auth | Courses | Lessons | Practice | Revision  │  │
    │  │  AI    | Users   | Admin   | Gamification       │  │
    │  └──────────────────────────────────────────────────┘  │
    └────────────────────────┬───────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐      ┌──────▼──────┐     ┌─────▼─────┐
    │PostgreSQL│      │    Redis     │     │  Object   │
    │ (Primary) │      │  (Cache /    │     │  Storage  │
    │           │      │   Queue)     │     │  (S3)     │
    └───────────┘      └─────────────┘     └───────────┘
         │
    ┌────▼──────────────────────────────────────────────┐
    │              AI Services (Swappable)                │
    │  ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │
    │  │ LLM API  │ │ Embedding│ │  Sandbox Executor │  │
    │  │ (OpenAI/ │ │  Model   │ │  (Isolated Docker) │  │
    │  │  Anthropic│ │          │ │                    │  │
    │  └──────────┘ └──────────┘ └───────────────────┘  │
    └────────────────────────────────────────────────────┘
```

---

## Bounded Contexts

### 1. Identity & Access (auth)
- User registration, login, JWT + refresh tokens
- OAuth2 providers (Google, GitHub)
- Role-based access (student, teacher, admin, superadmin)
- Profile management, avatar uploads
- Preferences & notification settings

### 2. Content Management (courses)
- Courses, modules, lessons hierarchy
- Rich content with Markdown, code blocks, diagrams
- Content versioning and draft/published states
- Tags, difficulty levels, prerequisites
- Search & filtering

### 3. Learning Experience (learning)
- Progress tracking per user per lesson
- Bookmarks, notes, highlights
- Resume/continue learning
- Reading progress
- Recently viewed history

### 4. Practice Engine (practice)
- Exercise types: output prediction, debugging, completion, refactoring, optimization
- Difficulty tiers: easy, medium, hard
- Hints system with progressive disclosure
- Solution validation
- Practice history & analytics
- Coding assessments

### 5. Revision System (revision)
- Spaced repetition algorithm (SM-2 enhanced)
- Flashcards generation & scheduling
- Weak topic detection via analytics
- Knowledge graph construction
- Revision planner & reminders
- Checkpoints & reinforcement

### 6. AI Services (ai)
- Swappable provider architecture (OpenAI, Anthropic, local models)
- AI Tutor for conversational learning
- AI Code Reviewer for practice submissions
- AI Debugger assistant
- AI Project Reviewer
- AI Interviewer (mock interviews)
- AI Career Advisor
- AI Roadmap Generator
- AI Learning Assistant
- AI Quiz/Explanation/Hint generation

### 7. Sandbox (sandbox)
- Isolated Docker containers per session
- Multi-language support
- Resource limits (CPU, memory, time, network)
- Filesystem isolation
- Network sandboxing
- Session lifecycle management
- Abuse prevention

### 8. Gamification (gamification)
- XP / Leveling system
- Achievements & Badges
- Daily streaks
- Leaderboards (global, course, weekly)
- Challenges & competitions
- Milestone rewards

### 9. Community (community)
- Discussion forums per lesson
- Q&A with voting
- Code sharing & reviews
- Study groups

### 10. Administration (admin)
- Dashboard with analytics
- Content CRUD
- User management & roles
- System configuration
- Feature flags
- Audit logs
- Usage reports

---

## Database Design Principles

1. **Normalized** — 3NF minimum; denormalized only where proven performance benefit.
2. **UUID Primary Keys** — All tables use UUIDs; no sequential ID leakage.
3. **Timestamps** — `created_at`, `updated_at` on every table; `deleted_at` for soft-delete where needed.
4. **Audit Trail** — Dedicated audit tables for sensitive mutations.
5. **Indexing** — Covering indexes for all query patterns; no over-indexing.
6. **Migrations** — Alembic for all schema changes; never raw SQL DDL in production.

---

## API Design Principles

1. **RESTful** — Resource-oriented URLs, proper HTTP methods.
2. **Versioning** — URL prefix: `/api/v1/`
3. **Pagination** — Cursor-based for large collections; offset for small.
4. **Filtering** — Query parameters with `filter[field]=value` syntax.
5. **Sorting** — `sort=field` and `sort=-field` for descending.
6. **Error Format** — Consistent JSON error responses with codes, messages, details.
7. **Rate Limiting** — Token bucket per user/IP; configurable tiers.
8. **Compression** — Brotli/gzip based on Accept-Encoding.

---

## Frontend Architecture

### Routes
```
/                          Landing page
/login                     Login
/signup                    Registration
/dashboard                 User dashboard
/courses                   Browse courses
/courses/[slug]            Course overview
/courses/[slug]/learn      Learning interface
/courses/[slug]/learn/[lesson]  Lesson page
/practice                  Practice hub
/practice/[id]             Practice exercise
/revision                  Revision dashboard
/revision/flashcards       Flashcard deck
/ai                        AI assistant hub
/ai/tutor                  AI Tutor chat
/ai/code-review            AI Code Reviewer
/profile                   User profile
/profile/settings          Account settings
/profile/certificates      User certificates
/admin                     Admin dashboard
/admin/courses             Course management
/admin/users               User management
/admin/analytics           Analytics
```

### Component Architecture
```
components/
├── ui/                    Design system primitives
│   ├── Button, Input, Card, Modal, Toast, etc.
├── layout/                Layout components
│   ├── AppShell, Sidebar, Header, Footer
├── learning/              Learning-specific components
│   ├── LessonViewer, CodeBlock, QuizWidget
├── practice/              Practice components
│   ├── CodeEditor, TestRunner, DiffViewer
├── revision/              Revision components
│   ├── Flashcard, SpacedRepetitionChart
├── ai/                    AI interface components
│   ├── ChatInterface, CodeReviewPanel
├── gamification/          Gamification components
│   ├── XPBar, Badge, StreakCounter
└── shared/                Shared utilities
    ├── SEO, Analytics, ErrorBoundary
```

---

## Security Architecture

1. **Authentication**: JWT access tokens (15 min) + refresh tokens (7 days, rotating)
2. **Password Storage**: Argon2id hashing
3. **CSRF**: Double-submit cookie pattern for browser clients
4. **CORS**: Strict origin allowlist
5. **Rate Limiting**: Per-endpoint, per-user, per-IP
6. **Input Validation**: Pydantic models for all request bodies
7. **Output Sanitization**: Context-aware escaping
8. **SQL Injection**: Parameterized queries via SQLAlchemy
9. **XSS**: Strict CSP headers; React's built-in escaping
10. **Sandbox**: gVisor/Docker isolation; no host network access
11. **Secrets**: Environment variables; never in code or VCS
12. **HTTPS**: Enforced via HSTS

---

## Deployment Architecture

### Backend (Render)
- Docker container
- Gunicorn + Uvicorn workers
- PostgreSQL managed database
- Redis managed instance
- Environment-based configuration
- Health check endpoint: `GET /api/health`

### Frontend (Vercel)
- Next.js with App Router
- ISR for course content pages
- SSR for dashboard/personalized pages
- Edge middleware for auth redirects
- Static asset optimization

### CI/CD (GitHub Actions)
- Lint → Test → Build → Deploy pipeline
- Alembic migrations run before deploy
- Smoke tests after deploy
- Rollback capability

---

## Monitoring & Observability

1. **Structured Logging**: JSON logs with correlation IDs
2. **Metrics**: Request latency, error rates, active users
3. **Alerting**: Error rate thresholds, API latency spikes
4. **Tracing**: Request ID propagation through all services
5. **Health Checks**: Liveness and readiness probes
