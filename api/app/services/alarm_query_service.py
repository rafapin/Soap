from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AlarmNotFoundError
from app.repositories.alarm_repository import AlarmRepository


class AlarmQueryService:
    def __init__(self, session: Session) -> None:
        self._repo = AlarmRepository(session)

    def get_alarm(self, alarm_id: int):
        alarm = self._repo.get_by_id(alarm_id)
        if alarm is None:
            raise AlarmNotFoundError(f"Alarm with id={alarm_id} not found")
        return alarm

    def list_alarms(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        criticality: Optional[str] = None,
        tag: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple:
        return self._repo.get_paginated(
            start_time=start_time,
            end_time=end_time,
            criticality=criticality,
            tag=tag,
            page=page,
            page_size=page_size,
        )
