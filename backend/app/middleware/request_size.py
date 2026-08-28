from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_413_CONTENT_TOO_LARGE
import structlog

logger = structlog.get_logger()


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10 MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        # Check content length header
        if "content-length" in request.headers:
            content_length = int(request.headers["content-length"])
            if content_length > self.max_size:
                logger.warning(
                    "Request size limit exceeded",
                    content_length=content_length,
                    max_size=self.max_size,
                    path=request.url.path,
                )
                return Response(
                    content="Request entity too large",
                    status_code=HTTP_413_CONTENT_TOO_LARGE,
                )

        # For chunked transfers, we would need to read the body, but that's expensive
        # Instead, we'll rely on the web server (nginx, etc.) to limit request size
        # or we can read the body in chunks if needed for specific endpoints
        
        return await call_next(request)