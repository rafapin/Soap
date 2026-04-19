from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from app.core.constants import CRITICALITY_MAPPING, STATE_MAPPING, MAX_TAG_LENGTH, MAX_MESSAGE_LENGTH


def normalize_criticality(value: Optional[str]) -> Optional[str]:
    """Map raw criticality strings to a canonical HIGH/MEDIUM/LOW value."""
    if value is None:
        return None
    stripped = str(value).strip()
    return CRITICALITY_MAPPING.get(stripped, None)


def normalize_state(value: Optional[str]) -> Optional[str]:
    """Map raw state strings to a canonical value."""
    if value is None:
        return None
    stripped = str(value).strip()
    return STATE_MAPPING.get(stripped, None)


def clean_string(value: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    """Strip whitespace, collapse internal spaces, truncate, return None if empty."""
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", str(value).strip())
    if not cleaned:
        return None
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned


def validate_temporal_consistency(
    event_time: Optional[datetime],
    ack_time: Optional[datetime],
    clear_time: Optional[datetime],
) -> list[str]:
    """Return a list of consistency violation messages (empty if all valid)."""
    errors: list[str] = []

    if event_time is None:
        errors.append("event_time is required")
        return errors  # cannot check relative times without event_time

    if ack_time is not None and ack_time < event_time:
        errors.append(f"ack_time ({ack_time}) is before event_time ({event_time})")

    if clear_time is not None and clear_time < event_time:
        errors.append(f"clear_time ({clear_time}) is before event_time ({event_time})")

    return errors
