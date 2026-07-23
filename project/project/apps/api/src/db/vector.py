from __future__ import annotations

from typing import Any

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator


class VectorType(TypeDecorator[list[float] | None]):
    """Vector storage that uses pgvector on PostgreSQL and JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def __init__(self, dimensions: int = 1536) -> None:
        self.dimensions = dimensions
        super().__init__()

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(JSON)

    def process_bind_param(self, value: list[float] | None, dialect: Any) -> Any:  # noqa: ARG002
        return value

    def process_result_value(self, value: Any, dialect: Any) -> list[float] | None:  # noqa: ARG002
        return value if isinstance(value, list) else None
