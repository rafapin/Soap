from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.alarm_repository import AlarmRepository


class MetricsService:
    def __init__(self, session: Session) -> None:
        self._repo = AlarmRepository(session)

    def top_tags(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10,
    ) -> list[dict]:
        rows = self._repo.get_top_tags(start_time=start_time, end_time=end_time, limit=limit)
        return [{"tag": tag, "alarm_count": count} for tag, count in rows]

    def summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tag: Optional[str] = None,
    ) -> dict:
        return self._repo.get_summary(start_time=start_time, end_time=end_time, tag=tag)

    def charts(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        criticality: Optional[str] = None,
        tag: Optional[str] = None,
        bucket: str = "day",
        limit: int = 10,
    ) -> dict:
        filters = dict(start_time=start_time, end_time=end_time, criticality=criticality, tag=tag)
        return {
            "timeline": self._repo.get_timeline_counts(bucket=bucket, **filters),
            "by_criticality": self._repo.get_group_counts("criticality", **filters),
            "by_state": self._repo.get_group_counts("state", **filters),
            "top_tags": self._repo.get_group_counts("tag", limit=limit, **filters),
            "by_plant": self._repo.get_group_counts("plant", limit=limit, **filters),
            "by_area": self._repo.get_group_counts("area", limit=limit, **filters),
            "by_priority": self._repo.get_group_counts("priority", **filters),
            "by_source_system": self._repo.get_group_counts("source_system", limit=limit, **filters),
        }
