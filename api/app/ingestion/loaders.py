from __future__ import annotations

from typing import Any

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.db.models.alarm import Alarm
from app.db.models.alarm_rejection import AlarmRejection
from app.db.models.ingestion_batch import IngestionBatch

logger = get_logger(__name__)


def create_ingestion_batch(session: Session, source_file_name: str, file_type: str) -> IngestionBatch:
    """Create a batch record with PENDING status and return it."""
    batch = IngestionBatch(
        source_file_name=source_file_name,
        file_type=file_type,
        status="IN_PROGRESS",
    )
    session.add(batch)
    session.flush()  # get the id without committing
    logger.info(f"Created ingestion batch id={batch.id} for {source_file_name}")
    return batch


def bulk_insert_alarms(session: Session, records: list[dict[str, Any]]) -> int:
    """
    Insert alarms in chunks using SQLAlchemy Core insert.
    Skips records that violate the unique business key (ON CONFLICT DO NOTHING).
    Returns the number of actually inserted rows.
    """
    if not records:
        return 0

    chunk_size = settings.batch_size
    inserted = 0

    for i in range(0, len(records), chunk_size):
        chunk = records[i : i + chunk_size]
        bind = session.get_bind()
        dialect_name = bind.dialect.name if bind is not None else "postgresql"
        if dialect_name == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            stmt = sqlite_insert(Alarm).values(chunk)
            stmt = stmt.on_conflict_do_nothing(index_elements=["external_alarm_id", "event_time", "tag"])
        else:
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(Alarm).values(chunk)
            stmt = stmt.on_conflict_do_nothing(constraint="uq_alarm_business_key")

        result = session.execute(stmt)
        inserted += max(int(result.rowcount or 0), 0)
        logger.debug(f"Inserted chunk {i // chunk_size + 1}: {len(chunk)} records attempted")

    return inserted


def bulk_insert_rejections(session: Session, batch_id: int, rejections: list[dict[str, Any]]) -> None:
    """Insert rejection records linked to the given batch."""
    if not rejections:
        return
    records = [
        {
            "batch_id": batch_id,
            "raw_payload": r["raw_payload"],
            "rejection_reason": r["rejection_reason"],
        }
        for r in rejections
    ]
    session.execute(insert(AlarmRejection), records)
    logger.info(f"Inserted {len(records)} rejection records for batch_id={batch_id}")


def finalize_batch(
    session: Session,
    batch: IngestionBatch,
    status: str,
    total_rows: int,
    inserted_rows: int,
    rejected_rows: int,
    error_message: str | None = None,
) -> None:
    """Update batch record with final counts and status."""
    batch.status = status
    batch.total_rows = total_rows
    batch.inserted_rows = inserted_rows
    batch.rejected_rows = rejected_rows
    batch.error_message = error_message
    session.add(batch)
    logger.info(
        f"Batch id={batch.id} finalized: status={status}, "
        f"total={total_rows}, inserted={inserted_rows}, rejected={rejected_rows}"
    )
