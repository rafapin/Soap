from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from app.core.logger import get_logger

logger = get_logger(__name__)


def read_csv(path: str | Path) -> pd.DataFrame:
    """Read a CSV file and return a raw DataFrame with all columns as strings."""
    path = Path(path)
    logger.info(f"Reading CSV file: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    logger.info(f"CSV loaded: {len(df)} rows, columns: {list(df.columns)}")
    return df


def read_json(path: str | Path) -> pd.DataFrame:
    """Read a JSON file (array of objects) and return a raw DataFrame."""
    path = Path(path)
    logger.info(f"Reading JSON file: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array at root level, got {type(data).__name__}")
    df = pd.DataFrame(data).astype(str)
    df = df.replace("None", "")
    df = df.replace("nan", "")
    logger.info(f"JSON loaded: {len(df)} rows, columns: {list(df.columns)}")
    return df


def detect_file_type(path: str | Path) -> str:
    """Return 'CSV' or 'JSON' based on file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return "CSV"
    if suffix == ".json":
        return "JSON"
    raise ValueError(f"Unsupported file type: {suffix}")


def read_file(path: str | Path) -> tuple[pd.DataFrame, str]:
    """Auto-detect file type and return (DataFrame, file_type)."""
    file_type = detect_file_type(path)
    if file_type == "CSV":
        return read_csv(path), file_type
    return read_json(path), file_type
