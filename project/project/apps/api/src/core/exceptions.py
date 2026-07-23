from __future__ import annotations

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    message: str
    code: str | None = None
    field: str | None = None


class DSirHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


def not_found(detail: str = "Not found", code: str | None = None) -> DSirHTTPException:
    return DSirHTTPException(status.HTTP_404_NOT_FOUND, detail, code)


def bad_request(detail: str = "Bad request", code: str | None = None) -> DSirHTTPException:
    return DSirHTTPException(status.HTTP_400_BAD_REQUEST, detail, code)


def forbidden(detail: str = "Forbidden", code: str | None = None) -> DSirHTTPException:
    return DSirHTTPException(status.HTTP_403_FORBIDDEN, detail, code)
