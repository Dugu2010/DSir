from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import time
import uuid
import structlog
from app.config import get_settings
from collections import defaultdict
from datetime import datetime, timedelta

settings = get_settings()
logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.time()

        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)

        duration_ms = (time.time() - start) * 1000
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        response.headers["X-Request-ID"] = request_id
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[datetime]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/api"):
            client_ip = request.client.host if request.client else "unknown"
            now = datetime.utcnow()
            window = timedelta(seconds=settings.RATE_LIMIT_GLOBAL_WINDOW)
            limit = settings.RATE_LIMIT_GLOBAL

            if path.startswith("/api/v1/auth"):
                window = timedelta(seconds=settings.RATE_LIMIT_AUTH_WINDOW)
                limit = settings.RATE_LIMIT_AUTH

            key = f"{client_ip}:{path}"
            cutoff = now - window
            self._requests[key] = [t for t in self._requests.get(key, []) if t > cutoff]

            if len(self._requests[key]) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                    headers={"Retry-After": str(window.seconds)},
                )

            self._requests[key].append(now)

        return await call_next(request)


def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=86400,
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
