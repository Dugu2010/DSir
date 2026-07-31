from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import check_db_connection, close_db_connection, engine, Base
from app.middleware import setup_middleware
from app.api import auth, users, courses, learning, practice, revision, ai as ai_routes, admin

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting DSir API server", environment=settings.ENVIRONMENT)
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
    description="DSir — The world's best AI-powered programming education platform",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

setup_middleware(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


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


# ── API Routes ──────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(practice.router, prefix="/api/v1")
app.include_router(revision.router, prefix="/api/v1")
app.include_router(ai_routes.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
