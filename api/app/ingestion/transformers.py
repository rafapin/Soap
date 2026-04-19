from __future__ import annotations

import re
from typing import Optional

import pandas as pd

from app.core.constants import (
    CRITICALITY_MAPPING,
    STATE_MAPPING,
    MAX_TAG_LENGTH,
    MAX_MESSAGE_LENGTH,
    MAX_SOURCE_SYSTEM_LENGTH,
)
from app.domain.validators import clean_string, normalize_criticality, normalize_state, validate_temporal_consistency
from app.ingestion.parsers import parse_datetime, parse_priority, parse_string
from app.core.logger import get_logger

logger = get_logger(__name__)

DEDUP_KEY_COLS = ["external_alarm_id", "event_time_parsed", "tag_clean"]


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip, lowercase, replace spaces with underscores."""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def transform_dataframe(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """
    Full transformation pipeline.

    Returns:
        valid_records: list of dicts ready for DB insertion
        rejected_records: list of dicts with fields: raw_payload, rejection_reason
    """
    df = _standardize_columns(df)

    valid: list[dict] = []
    rejected: list[dict] = []
    seen_keys: set[tuple] = set()

    for idx, row in df.iterrows():
        raw_payload = row.to_json(force_ascii=False)
        errors: list[str] = []

        # Parse and clean all fields
        external_alarm_id = parse_string(row.get("external_alarm_id"))
        source_system = clean_string(parse_string(row.get("source_system")), MAX_SOURCE_SYSTEM_LENGTH)
        tag = clean_string(parse_string(row.get("tag")), MAX_TAG_LENGTH)
        message = clean_string(parse_string(row.get("message")), MAX_MESSAGE_LENGTH)
        priority = parse_priority(row.get("priority"))
        criticality_raw = parse_string(row.get("criticality"))
        criticality = normalize_criticality(criticality_raw)
        state_raw = parse_string(row.get("state"))
        state = normalize_state(state_raw)
        plant = clean_string(parse_string(row.get("plant")), 100)
        area = clean_string(parse_string(row.get("area")), 100)
        equipment = clean_string(parse_string(row.get("equipment")), 100)

        event_time = parse_datetime(row.get("event_time"))
        ack_time = parse_datetime(row.get("ack_time"))
        clear_time = parse_datetime(row.get("clear_time"))

        # Validation rules
        if event_time is None:
            errors.append("event_time is required and could not be parsed")

        if tag is None:
            errors.append("tag is required")

        if criticality_raw and criticality is None:
            errors.append(f"criticality '{criticality_raw}' is not in the valid catalogue (HIGH/MEDIUM/LOW)")

        if criticality is None and not criticality_raw:
            errors.append("criticality is required")

        # Temporal consistency (only if event_time parsed)
        if event_time is not None:
            time_errors = validate_temporal_consistency(event_time, ack_time, clear_time)
            errors.extend(time_errors)

        if errors:
            rejected.append({"raw_payload": raw_payload, "rejection_reason": "; ".join(errors)})
            continue

        # Duplicate check
        dedup_key = (external_alarm_id or "", str(event_time), tag or "")
        if dedup_key in seen_keys:
            rejected.append(
                {
                    "raw_payload": raw_payload,
                    "rejection_reason": f"Duplicate record: key={dedup_key}",
                }
            )
            continue
        seen_keys.add(dedup_key)

        valid.append(
            {
                "external_alarm_id": external_alarm_id,
                "source_system": source_system,
                "tag": tag,
                "message": message,
                "priority": priority,
                "criticality": criticality,
                "state": state,
                "plant": plant,
                "area": area,
                "equipment": equipment,
                "event_time": event_time,
                "ack_time": ack_time,
                "clear_time": clear_time,
            }
        )

    logger.info(f"Transformation complete: {len(valid)} valid, {len(rejected)} rejected")
    return valid, rejected
