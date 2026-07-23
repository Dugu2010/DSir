# Folder Structure: DSir

```
dsir/
├── apps/
│   ├── web/                    # Next.js frontend
│   │   ├── app/                # App router
│   │   ├── components/         # Reusable UI components
│   │   ├── features/           # Feature-specific modules
│   │   ├── lib/                # Utilities and API clients
│   │   ├── styles/             # Global styles
│   │   └── public/             # Static assets
│   └── api/                    # FastAPI backend
│       ├── src/
│       │   ├── api/            # API route modules
│       │   ├── core/           # Config, security, dependencies
│       │   ├── models/         # SQLAlchemy/Pydantic models
│       │   ├── services/       # Business logic
│       │   ├── db/             # Database setup and migrations
│       │   ├── ai/             # AI provider abstraction
│       │   ├── revision/       # Revision engine
│       │   ├── mastery/        # Mastery engine
│       │   ├── projects/       # Project engine
│       │   └── main.py         # Application entry point
│       ├── tests/              # Backend tests
│       ├── Dockerfile
│       └── pyproject.toml
├── packages/
│   ├── shared/                 # Shared types and utilities
│   └── ui/                     # Shared UI components
├── docs/                       # Design documents
├── infra/
│   ├── docker/                 # Docker Compose and configs
│   └── k8s/                    # Kubernetes manifests
├── scripts/                    # Automation scripts
├── README.md
├── docker-compose.yml
└── turbo.json                  # Monorepo task orchestration
```

## Conventions

- Each domain has its own module under `apps/api/src/`
- Frontend features are organized by domain under `apps/web/features/`
- Shared code lives in `packages/`
- Design documents live in `docs/` and are updated as the system evolves
