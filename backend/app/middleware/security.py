from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import structlog

from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # HSTS is only meaningful over HTTPS. Render terminates TLS before
        # forwarding to the Python service, so production responses should
        # advertise the HTTPS policy without affecting local development.
        if settings.ENVIRONMENT.lower() == "production" and request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # This is an API response, not the Next.js application shell. Keep the
        # policy strict and avoid the previous blanket https:/unsafe-eval grants.
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            "connect-src 'self' https: wss:; "
            "frame-ancestors 'none'; "
            "base-uri 'none'; "
            "form-action 'none'"
        )

        return response
