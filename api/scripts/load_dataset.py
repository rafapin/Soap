"""
Load a dataset file into the database using the full ETL pipeline.

Run:
  python scripts/load_dataset.py --file data/raw/alarms_dataset.csv
  python scripts/load_dataset.py --file data/raw/alarms_dataset.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logger import get_logger
from app.db.session import SessionLocal
from app.services.ingestion_service import run_ingestion

logger = get_logger(__name__)


def main(file_path: str) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    print(f"Starting ingestion for: {path}")
    with SessionLocal() as session:
        summary = run_ingestion(session, path)

    print("\n-- Ingestion Summary ------------------------------")
    for k, v in summary.items():
        print(f"  {k:<20} {v}")
    print("---------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load SCADA alarm dataset into the database")
    parser.add_argument(
        "--file",
        type=str,
        default="data/raw/alarms_dataset.csv",
        help="Path to the dataset file (CSV or JSON)",
    )
    args = parser.parse_args()
    main(args.file)
