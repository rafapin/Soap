from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.ingestion_batch import IngestionBatch


class BatchRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, batch_id: int) -> IngestionBatch | None:
        return self._session.get(IngestionBatch, batch_id)

    def list_all(self) -> list[IngestionBatch]:
        from sqlalchemy import select
        return list(self._session.scalars(select(IngestionBatch).order_by(IngestionBatch.processed_at.desc())).all())
