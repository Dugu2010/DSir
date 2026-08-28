"""
Observability module for DSir backend.
Handles structured metrics (Prometheus) and OpenTelemetry tracing.
"""
import re
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# ── Prometheus metrics (always available) ───────────────────────────

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "status_code"],
)

REQUEST_SIZE = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
)

RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
)

DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
)

# ── OpenTelemetry tracing (optional, never fatal) ───────────────────

_trace_provider = None
_tracer = None


def setup_opentelemetry():
    """Setup OpenTelemetry tracing. Failures are logged but never fatal."""
    global _trace_provider, _tracer
    if _trace_provider is not None:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({
            "service.name": settings.APP_NAME,
            "service.version": settings.APP_VERSION,
            "deployment.environment": settings.ENVIRONMENT,
        })

        _trace_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(_trace_provider)
        _tracer = trace.get_tracer(__name__)

        # Enable optional SQLAlchemy / Redis instrumentation without breaking startup
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            SQLAlchemyInstrumentor().instrument()
        except Exception as e:  # pragma: no cover
            logger.warning("sqlalchemy.instrumentation.failed", error=str(e))

        try:
            from opentelemetry.instrumentation.redis import RedisInstrumentor
            RedisInstrumentor().instrument()
        except Exception as e:  # pragma: no cover
            logger.warning("redis.instrumentation.failed", error=str(e))

        logger.info("opentelemetry.initialized")
    except Exception as e:  # pragma: no cover
        logger.warning("opentelemetry.setup.failed", error=str(e))


def get_tracer():
    """Return the global tracer (may be None if OTel unavailable)."""
    return _tracer


def render_prometheus_metrics() -> bytes:
    """Render all registered Prometheus metrics in exposition format."""
    return generate_latest()


# Matches UUIDs and plain numeric path segments (e.g. /courses/abc-123 → /courses/:id)
_UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_NUMERIC_SEGMENT_RE = re.compile(r"/\d+")
_NORMALIZED_ID = "/:id"


def _resolve_endpoint(request: Request) -> str:
    """Resolve the route template (e.g. `/api/v1/learn/{course_slug}/{module_slug}/{lesson_slug}`)
    for a request, keeping Prometheus label cardinality bounded even for routes with dynamic
    path parameters. Handles both classic router structures and FastAPI's lazy
    `_IncludedRouter` (include_router). Falls back to a normalized raw path when no route
    matches (e.g. 404/405)."""
    router = request.scope.get("router")
    routes = getattr(router, "routes", None) if router is not None else None
    if routes:
        for route in routes:
            # FastAPI (>= 0.140): include_router creates lazy _IncludedRouter entries.
            # Their effective contexts expose the fully-prefixed route templates.
            contexts = getattr(route, "effective_route_contexts", None)
            if callable(contexts):
                for ctx in contexts():
                    sroute = getattr(ctx, "starlette_route", None)
                    if sroute is None:
                        continue
                    match, _ = sroute.matches(request.scope)
                    if match == Match.FULL and sroute.path:
                        return sroute.path
                continue
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                path = getattr(route, "path", None)
                if path:
                    return path
    # No route matched (e.g. 404/405 or middleware before routing) — normalize the path
    return _NUMERIC_SEGMENT_RE.sub(_NORMALIZED_ID, _UUID_RE.sub(":id", request.url.path))


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics and traces."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        tracer = get_tracer()
        span = None
        if tracer is not None:
            span = tracer.start_as_current_span(f"{request.method} {_resolve_endpoint(request)}")
            span = span.__enter__()

        start_time = time.time()

        request_size = 0
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                request_size = int(content_length)
            except (ValueError, TypeError):
                pass

        try:
            response = await call_next(request)
        except Exception:
            if span is not None:
                span.__exit__(None, None, None)
            raise

        latency = time.time() - start_time

        endpoint = _resolve_endpoint(request)
        labels = {
            "method": request.method,
            "endpoint": endpoint,
            "status_code": str(response.status_code),
        }
        REQUEST_COUNT.labels(**labels).inc()
        REQUEST_LATENCY.labels(**labels).observe(latency)
        if request_size > 0:
            REQUEST_SIZE.labels(method=request.method, endpoint=endpoint).observe(request_size)

        if span is not None:
            if response.status_code >= 400:
                span.set_attribute("http.status_code", response.status_code)
            span.__exit__(None, None, None)

        trace_id = None
        if span is not None:
            ctx = getattr(span, "get_span_context", lambda: None)()
            if ctx is not None and hasattr(ctx, "trace_id"):
                trace_id = ctx.trace_id
        if trace_id:
            response.headers["X-Trace-ID"] = format(trace_id, "032x")

        return response


def instrument_fastapi(app):
    """Instrument FastAPI app with OpenTelemetry (non-fatal on failure)."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor().instrument_app(app)
        logger.info("fastapi.instrumented")
    except Exception as e:  # pragma: no cover
        logger.warning("fastapi.instrumentation.failed", error=str(e))
