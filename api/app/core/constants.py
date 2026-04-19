from __future__ import annotations

# ── Catalogue values ──────────────────────────────────────────────────────────
VALID_CRITICALITIES = {"HIGH", "MEDIUM", "LOW"}

CRITICALITY_MAPPING: dict[str, str] = {
    # HIGH variants
    "HIGH": "HIGH",
    "High": "HIGH",
    "high": "HIGH",
    "H": "HIGH",
    # MEDIUM variants
    "MEDIUM": "MEDIUM",
    "Medium": "MEDIUM",
    "medium": "MEDIUM",
    "MED": "MEDIUM",
    "Med": "MEDIUM",
    "M": "MEDIUM",
    # LOW variants
    "LOW": "LOW",
    "Low": "LOW",
    "low": "LOW",
    "L": "LOW",
}

VALID_STATES = {"ACTIVE", "ACKNOWLEDGED", "CLEARED", "SHELVED"}

STATE_MAPPING: dict[str, str] = {
    "ACTIVE": "ACTIVE",
    "Active": "ACTIVE",
    "active": "ACTIVE",
    "ACK": "ACKNOWLEDGED",
    "ACKNOWLEDGED": "ACKNOWLEDGED",
    "Acknowledged": "ACKNOWLEDGED",
    "acknowledged": "ACKNOWLEDGED",
    "CLEARED": "CLEARED",
    "Cleared": "CLEARED",
    "cleared": "CLEARED",
    "SHELVED": "SHELVED",
    "Shelved": "SHELVED",
    "shelved": "SHELVED",
}

# ── ETL constants ─────────────────────────────────────────────────────────────
DEFAULT_BATCH_SIZE = 500
MAX_TAG_LENGTH = 200
MAX_MESSAGE_LENGTH = 1000
MAX_SOURCE_SYSTEM_LENGTH = 100

# ── Date parse formats ────────────────────────────────────────────────────────
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
]

# ── API constants ─────────────────────────────────────────────────────────────
DEFAULT_TOP_TAGS_LIMIT = 10
MAX_TOP_TAGS_LIMIT = 50
