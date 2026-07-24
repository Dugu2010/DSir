from __future__ import annotations

import json
from typing import cast

import pytest
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from src.main import (
    global_exception_handler,
    http_exception_handler,
    sqlalchemy_error_handler,
    validation_exception_handler,
    value_error_handler,
)


def _body_json(response: object) -> object:
    body = cast(bytes, response.body).decode()  # type: ignore[attr-defined]
    return json.loads(body)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_http_exception_handler_propagates_headers() -> None:
    exc = HTTPException(
        status_code=404,
        detail="not found",
        headers={"x-custom": "value"},
    )
    response = await http_exception_handler(None, exc)  # type: ignore[arg-type]
    body = _body_json(response)
    assert response.status_code == 404
    assert response.headers["x-custom"] == "value"
    assert body == {"detail": "not found"}


@pytest.mark.asyncio
async def test_validation_exception_handler_returns_422() -> None:
    errors = [
        {"loc": ("field",), "msg": "required", "type": "value_error.missing"},
    ]
    exc = RequestValidationError(errors=errors)
    response = await validation_exception_handler(None, exc)  # type: ignore[arg-type]
    body = _body_json(response)
    assert response.status_code == 422
    # JSON round-trips tuples as lists.
    assert body == {"detail": [{"loc": ["field"], "msg": "required", "type": "value_error.missing"}]}


@pytest.mark.asyncio
async def test_value_error_handler_returns_400() -> None:
    response = await value_error_handler(None, ValueError("bad input"))  # type: ignore[arg-type]
    body = _body_json(response)
    assert response.status_code == 400
    assert body == {"detail": "bad input"}


@pytest.mark.asyncio
async def test_sqlalchemy_error_handler_returns_500() -> None:
    response = await sqlalchemy_error_handler(None, SQLAlchemyError("db failed"))  # type: ignore[arg-type]
    body = _body_json(response)
    assert response.status_code == 500
    assert body == {"detail": "Internal server error"}


@pytest.mark.asyncio
async def test_global_exception_handler_returns_500() -> None:
    response = await global_exception_handler(None, RuntimeError("boom"))  # type: ignore[arg-type]
    body = _body_json(response)
    assert response.status_code == 500
    assert body == {"detail": "Internal server error"}
