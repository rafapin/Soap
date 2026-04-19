from __future__ import annotations

from datetime import datetime
from typing import Optional

from dateutil import parser as dateutil_parser

from app.core.constants import DATE_FORMATS
from app.core.logger import get_logger

logger = get_logger(__name__)

_EMPTY_VALUES = {"", "nan", "none", "null", "n/a", "na", "NaT"}


def _is_empty(value: str) -> bool:
    return str(value).strip().lower() in _EMPTY_VALUES


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Try parsing a datetime string using a list of known formats,
    then fall back to dateutil. Returns None if value is empty or unparseable.
    """
    if value is None or _is_empty(str(value)):
        return None

    raw = str(value).strip()

    # Try known formats first (fast path)
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    # Fall back to dateutil (handles timezone-aware strings, etc.)
    try:
        dt = dateutil_parser.parse(raw)
        # Normalize to naive UTC
        if dt.tzinfo is not None:
            dt = dt.utctimetuple()
            dt = datetime(*dt[:6])
        return dt
    except Exception:
        logger.debug(f"Could not parse datetime value: {raw!r}")
        return None


def parse_priority(value: Optional[str]) -> Optional[int]:
    """
    Convert priority to integer. Returns None if empty or not convertible.
    Float-like strings (e.g. '3.0') are accepted.
    """
    if value is None or _is_empty(str(value)):
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def parse_string(value: Optional[str]) -> Optional[str]:
    """Strip whitespace; return None if empty."""
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped if stripped and stripped.lower() not in _EMPTY_VALUES else None
