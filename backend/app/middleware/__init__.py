from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import time
import uuid
import structlog
from app.config import get_settings
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.compression import GZipMiddleware
from app.middleware.request_size import RequestSizeLimitMiddleware

settings = get_settings()
logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.time()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.unbind_contextvars("request_id")

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

    @staticmethod
    def _client_key(request: Request) -> str:
        # Render's documented edge setup provides CF-Connecting-IP from
        # Cloudflare. Unlike X-Forwarded-For, it is overwritten at the edge.
        client_ip = request.headers.get("cf-connecting-ip")
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        return client_ip.strip() or "unknown"

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api"):
            return await call_next(request)

        now = datetime.now(timezone.utc)
        window_seconds = settings.RATE_LIMIT_GLOBAL_WINDOW
        limit = settings.RATE_LIMIT_GLOBAL
        if path.startswith("/api/v1/auth"):
            window_seconds = settings.RATE_LIMIT_AUTH_WINDOW
            limit = settings.RATE_LIMIT_AUTH

        key = f"{self._client_key(request)}:{path}"
        cutoff = now - timedelta(seconds=window_seconds)
        bucket = self._requests.get(key, [])
        bucket = [t for t in bucket if t > cutoff]
        self._requests[key] = bucket

        if len(bucket) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(window_seconds)},
            )

        bucket.append(now)

        # Bound in-memory growth on long-lived workers. Expired buckets are
        # cheap to discard and a hard cap prevents an attacker from creating
        # millions of unique keys.
        if len(self._requests) > 10000:
            stale_before = now - timedelta(seconds=max(window_seconds, settings.RATE_LIMIT_GLOBAL_WINDOW))
            for existing_key, timestamps in list(self._requests.items()):
                if not timestamps or timestamps[-1] <= stale_before:
                    self._requests.pop(existing_key, None)

        return await call_next(request)


def setup_middleware(app: FastAPI):
    app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
        max_age=86400,
    )

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=500)
    app.add_middleware(RequestLoggingMiddleware)
