from __future__ import annotations


class ScadaBaseError(Exception):
    """Base error for all domain exceptions."""

    def __init__(self, message: str, details: list[str] | None = None) -> None:
        self.message = message
        self.details = details or []
        super().__init__(message)


class AlarmNotFoundError(ScadaBaseError):
    """Raised when an alarm does not exist."""


class ValidationError(ScadaBaseError):
    """Raised when input validation fails at the domain level."""


class IngestionError(ScadaBaseError):
    """Raised when a fatal error occurs during the ingestion pipeline."""


class DatabaseError(ScadaBaseError):
    """Raised when an unexpected database-level error occurs."""
