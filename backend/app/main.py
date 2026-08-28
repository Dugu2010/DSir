from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import check_db_connection, close_db_connection, engine, Base
from app.middleware import setup_middleware
from app.observability import setup_opentelemetry, instrument_fastapi, ObservabilityMiddleware
from app.chaos import setup_chaos_middleware
from app.exceptions import setup_exception_handlers
from app.api import auth, users, courses, learning, practice, revision, ai as ai_routes, admin, quizzes, discussions, leaderboard

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DSir API server", environment=settings.ENVIRONMENT)
    setup_opentelemetry()
    setup_chaos_middleware(app)
    db_ok = await check_db_connection()
    if db_ok:
        logger.info("Database connection established")
    else:
        logger.warning("Database connection failed — server starting anyway")
    yield
    logger.info("Shutting down DSir API server")
    await close_db_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""DSir — The world's best AI-powered programming education platform
    
    ## Features
    
    * **Interactive Lessons** - Hands-on coding exercises with instant feedback
    * **AI-Powered Tutoring** - Personalized help from AI tutors
    * **Spaced Repetition** - Smart revision system for long-term retention
    * **Practice Engine** - Variety of exercise types to build skills
    * **Gamification** - XP, levels, achievements, and leaderboards
    * **Career Guidance** - Job preparation and interview practice
    
    ## Authentication
    
    Most endpoints require authentication. Use the `/auth/login` endpoint to obtain
    an access token, then include it in the Authorization header:
    
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    ## Rate Limiting
    
    API requests are rate-limited to prevent abuse. Different endpoints have
    different limits based on their sensitivity.
    
    ## Error Handling
    
    All errors follow a standardized format:
    
    ```json
    {
        "error": "ErrorType",
        "message": "Human-readable error message",
        "error_code": "ERROR_CODE",
        "details": {...},
        "path": "/api/v1/endpoint",
        "timestamp": "2023-01-01T00:00:00Z"
    }
    ```
    """,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    contact={
        "name": "DSir Support",
        "url": "https://dsir.dev/support",
        "email": "support@dsir.dev",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://dsir.dev/terms",
)

# Add observability middleware first to capture all requests
app.add_middleware(ObservabilityMiddleware)

setup_middleware(app)

# Instrument app with OpenTelemetry
instrument_fastapi(app)

# Setup standardized exception handlers
setup_exception_handlers(app)


# ── Health ──────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/api/health/ready")
async def readiness_check():
    db_ok = await check_db_connection()
    if not db_ok:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    return {"status": "ready"}


# ── Metrics ────────────────────────────────────────────────────────

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (plain-text exposition format)."""
    from app.observability import render_prometheus_metrics
    return Response(
        content=render_prometheus_metrics(),
        media_type="text/plain",
    )


# ── API Routes ──────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(practice.router, prefix="/api/v1")
app.include_router(revision.router, prefix="/api/v1")
app.include_router(ai_routes.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(quizzes.router, prefix="/api/v1")
app.include_router(discussions.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")
