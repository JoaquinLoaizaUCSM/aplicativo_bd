"""Modelos para representar resultados consistentes de operaciones CRUD."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class OperationStatus(str, Enum):
    """Estado normalizado para operaciones de base de datos."""

    SUCCESS = "success"
    NOT_FOUND = "not_found"
    DUPLICATE = "duplicate"
    VALIDATION_ERROR = "validation_error"
    ERROR = "error"


@dataclass(slots=True)
class OperationResult:
    """Encapsula el resultado de un procedimiento almacenado."""

    status: OperationStatus
    message: str
    data: Optional[Any] = None

    @property
    def ok(self) -> bool:
        return self.status == OperationStatus.SUCCESS

    @classmethod
    def success(cls, message: str, data: Optional[Any] = None) -> "OperationResult":
        return cls(OperationStatus.SUCCESS, message, data)

    @classmethod
    def failure(
        cls,
        status: OperationStatus,
        message: str,
        data: Optional[Any] = None,
    ) -> "OperationResult":
        if status == OperationStatus.SUCCESS:
            raise ValueError("Use success() para resultados exitosos")
        return cls(status, message, data)
