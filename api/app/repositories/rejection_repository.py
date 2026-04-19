from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.alarm_rejection import AlarmRejection


class RejectionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_batch_id(self, batch_id: int) -> list[AlarmRejection]:
        stmt = select(AlarmRejection).where(AlarmRejection.batch_id == batch_id)
        return list(self._session.scalars(stmt).all())
