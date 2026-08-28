import gzip
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
import structlog

logger = structlog.get_logger()


class GZipMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, minimum_size: int = 500):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Skip compression for certain conditions
        if (
            response.status_code < 200
            or response.status_code >= 300
            or "content-encoding" in response.headers
            or not self.should_compress(request, response)
        ):
            return response

        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Skip if too small
        if len(response_body) < self.minimum_size:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Compress the body
        compressed_body = gzip.compress(response_body)
        
        # Update headers
        headers = dict(response.headers)
        headers.update(
            {
                "content-encoding": "gzip",
                "content-length": str(len(compressed_body)),
                "vary": "Accept-Encoding",
            }
        )
        
        # Remove content-length if it was set (we're overriding it)
        if "content-length" in headers:
            del headers["content-length"]
        
        return StreamingResponse(
            content=[compressed_body],
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
        )

    def should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed."""
        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False
        
        # Check content type
        content_type = response.headers.get("content-type", "")
        if not content_type:
            return False
        
        # Compress these types
        compressible_types = [
            "application/json",
            "application/javascript",
            "text/json",
            "text/javascript",
            "text/plain",
            "text/html",
            "text/css",
            "text/xml",
            "application/xml",
        ]
        
        return any(ct in content_type for ct in compressible_types)