"""
Standardized exception handling for DSir backend.
"""
from datetime import datetime
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import structlog
from sqlalchemy.exc import SQLAlchemyError

logger = structlog.get_logger()


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    path: Optional[str] = None
    timestamp: str


class DSirException(HTTPException):
    """Base exception for DSir application."""
    
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        self.error = error
        self.message = message
        self.details = details
        self.error_code = error_code


class ValidationException(DSirException):
    """Exception for validation errors."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "VALIDATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="ValidationError",
            message=message,
            details=details,
            error_code=error_code,
        )


class AuthenticationException(DSirException):
    """Exception for authentication errors."""
    
    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "AUTHENTICATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="AuthenticationError",
            message=message,
            details=details,
            error_code=error_code,
        )


class AuthorizationException(DSirException):
    """Exception for authorization errors."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "AUTHORIZATION_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="AuthorizationError",
            message=message,
            details=details,
            error_code=error_code,
        )


class NotFoundException(DSirException):
    """Exception for resource not found errors."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "NOT_FOUND_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="NotFoundError",
            message=message,
            details=details,
            error_code=error_code,
        )


class ConflictException(DSirException):
    """Exception for resource conflict errors."""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "CONFLICT_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="ConflictError",
            message=message,
            details=details,
            error_code=error_code,
        )


class RateLimitException(DSirException):
    """Exception for rate limit errors."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "RATE_LIMIT_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error="RateLimitError",
            message=message,
            details=details,
            error_code=error_code,
        )


class InternalServerException(DSirException):
    """Exception for internal server errors."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None,
        error_code: str = "INTERNAL_SERVER_ERROR",
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="InternalServerError",
            message=message,
            details=details,
            error_code=error_code,
        )


async def dsir_exception_handler(request: Request, exc: DSirException) -> JSONResponse:
    """Handle DSir exceptions and return standardized error response."""
    logger.error(
        "dsir_exception",
        error=exc.error,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        path=request.url.path,
        method=request.method,
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        message=exc.message,
        details=exc.details,
        error_code=exc.error_code,
        path=str(request.url.path),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions and convert to standardized format."""
    logger.error(
        "http_exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    
    error_response = ErrorResponse(
        error="HTTPError",
        message=str(exc.detail),
        error_code=f"HTTP_{exc.status_code}",
        path=str(request.url.path),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    
    error_response = ErrorResponse(
        error="InternalServerError",
        message="An internal server error occurred",
        error_code="INTERNAL_SERVER_ERROR",
        path=str(request.url.path),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )


async def dependency_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle failures of external dependencies (database, cache, etc.).

    Maps SQLAlchemy/Redis connection failures to 503 Service Unavailable so
    upstream clients can retry with backoff instead of treating the failure
    as an internal defect. The full traceback is still logged for operators.
    """
    logger.error(
        "dependency_unavailable",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )

    error_response = ErrorResponse(
        error="ServiceUnavailable",
        message="A required service is temporarily unavailable",
        error_code="DEPENDENCY_UNAVAILABLE",
        path=str(request.url.path),
        timestamp=datetime.utcnow().isoformat() + "Z",
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response.model_dump(exclude_none=True),
    )


def setup_exception_handlers(app):
    """Setup exception handlers for FastAPI app."""
    app.add_exception_handler(DSirException, dsir_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, dependency_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    logger.info("Exception handlers configured")