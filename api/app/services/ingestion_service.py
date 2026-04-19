from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.exceptions import IngestionError
from app.core.logger import get_logger
from app.ingestion.loaders import (
    bulk_insert_alarms,
    bulk_insert_rejections,
    create_ingestion_batch,
    finalize_batch,
)
from app.ingestion.readers import read_file
from app.ingestion.transformers import transform_dataframe

logger = get_logger(__name__)


def run_ingestion(session: Session, file_path: str | Path) -> dict:
    """
    Full ETL pipeline for a single file.

    Returns a summary dict with batch_id, total, inserted, rejected.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise IngestionError(f"File not found: {file_path}")

    file_type = file_path.suffix.upper().lstrip(".")
    batch = create_ingestion_batch(session, str(file_path.name), file_type)

    try:
        df, detected_type = read_file(file_path)
        total_rows = len(df)

        valid_records, rejected_records = transform_dataframe(df)

        # Persist valid alarms (bulk, on-conflict-do-nothing)
        inserted = bulk_insert_alarms(session, valid_records)

        # Persist rejections
        bulk_insert_rejections(session, batch.id, rejected_records)

        finalize_batch(
            session,
            batch,
            status="COMPLETED",
            total_rows=total_rows,
            inserted_rows=inserted,
            rejected_rows=len(rejected_records),
        )
        session.commit()

        summary = {
            "batch_id": batch.id,
            "source_file": str(file_path.name),
            "total_rows": total_rows,
            "inserted_rows": inserted,
            "rejected_rows": len(rejected_records),
            "status": "COMPLETED",
        }
        logger.info(f"Ingestion complete: {summary}")
        return summary

    except Exception as exc:
        session.rollback()
        finalize_batch(
            session,
            batch,
            status="FAILED",
            total_rows=0,
            inserted_rows=0,
            rejected_rows=0,
            error_message=str(exc),
        )
        session.commit()
        logger.error(f"Ingestion failed for batch {batch.id}: {exc}")
        raise IngestionError(str(exc)) from exc
