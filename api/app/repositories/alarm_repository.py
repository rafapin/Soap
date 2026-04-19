from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import Session

from app.db.models.alarm import Alarm


class AlarmRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _apply_filters(
        self,
        stmt,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        criticality: Optional[str] = None,
        tag: Optional[str] = None,
    ):
        if start_time:
            stmt = stmt.where(Alarm.event_time >= start_time)
        if end_time:
            stmt = stmt.where(Alarm.event_time <= end_time)
        if criticality:
            stmt = stmt.where(Alarm.criticality == criticality)
        if tag:
            stmt = stmt.where(Alarm.tag.ilike(f"%{tag}%"))
        return stmt

    def get_by_id(self, alarm_id: int) -> Optional[Alarm]:
        stmt = select(Alarm).where(Alarm.id == alarm_id)
        return self._session.scalars(stmt).first()

    def get_paginated(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        criticality: Optional[str] = None,
        tag: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Alarm], int]:
        """Return (items, total_count) for the given filters."""
        stmt = self._apply_filters(
            select(Alarm),
            start_time=start_time,
            end_time=end_time,
            criticality=criticality,
            tag=tag,
        )
        count_stmt = self._apply_filters(
            select(func.count()).select_from(Alarm),
            start_time=start_time,
            end_time=end_time,
            criticality=criticality,
            tag=tag,
        )

        total = self._session.scalar(count_stmt) or 0
        items = self._session.scalars(
            stmt.order_by(Alarm.event_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        return list(items), total

    def get_top_tags(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10,
    ) -> list[tuple[str, int]]:
        """Return [(tag, count)] ordered by count desc."""
        stmt = (
            select(Alarm.tag, func.count(Alarm.id).label("alarm_count"))
            .group_by(Alarm.tag)
            .order_by(func.count(Alarm.id).desc())
            .limit(limit)
        )
        if start_time:
            stmt = stmt.where(Alarm.event_time >= start_time)
        if end_time:
            stmt = stmt.where(Alarm.event_time <= end_time)

        rows = self._session.execute(stmt).all()
        return [(row.tag, row.alarm_count) for row in rows]

    def get_summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tag: Optional[str] = None,
    ) -> dict:
        filters = dict(start_time=start_time, end_time=end_time, tag=tag)

        total_alarms = self._session.scalar(
            self._apply_filters(select(func.count()).select_from(Alarm), **filters)
        ) or 0

        criticality_value = func.coalesce(Alarm.criticality, "UNKNOWN")
        criticality_rows = self._session.execute(
            self._apply_filters(
                select(
                    criticality_value.label("value"),
                    func.count(Alarm.id).label("count"),
                ).group_by(criticality_value).order_by(criticality_value),
                **filters,
            )
        ).all()
        by_criticality = {row.value: int(row.count) for row in criticality_rows}

        state_value = func.coalesce(Alarm.state, "UNKNOWN")
        state_rows = self._session.execute(
            self._apply_filters(
                select(
                    state_value.label("value"),
                    func.count(Alarm.id).label("count"),
                ).group_by(state_value).order_by(state_value),
                **filters,
            )
        ).all()
        by_state = {row.value: int(row.count) for row in state_rows}

        latest_event_time = self._session.scalar(
            self._apply_filters(select(func.max(Alarm.event_time)), **filters)
        )

        return {
            "total_alarms": int(total_alarms),
            "by_criticality": by_criticality,
            "by_state": by_state,
            "latest_event_time": latest_event_time,
        }

    def get_timeline_counts(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        criticality: Optional[str] = None,
        tag: Optional[str] = None,
        bucket: str = "day",
    ) -> list[dict]:
        """Return alarm counts grouped by day or hour."""
        bind = self._session.get_bind()
        dialect_name = bind.dialect.name if bind is not None else "postgresql"

        if dialect_name == "sqlite":
            period_expr = func.strftime("%Y-%m-%d %H:00", Alarm.event_time) if bucket == "hour" else func.strftime(
                "%Y-%m-%d", Alarm.event_time
            )
        else:
            period_format = "YYYY-MM-DD HH24:00" if bucket == "hour" else "YYYY-MM-DD"
            period_expr = func.to_char(func.date_trunc(bucket, Alarm.event_time), period_format)

        period = period_expr.label("period")
        count_expr = func.count(Alarm.id).label("alarm_count")
        stmt = self._apply_filters(
            select(period, count_expr).group_by(period).order_by(period),
            start_time=start_time,
            end_time=end_time,
            criticality=criticality,
            tag=tag,
        )
        rows = self._session.execute(stmt).all()
        return [{"period": str(row.period), "alarm_count": int(row.alarm_count)} for row in rows]

    def get_group_counts(
        self,
        field_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        criticality: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:
        """Return value/count pairs for a whitelisted alarm field."""
        allowed_fields = {
            "criticality": Alarm.criticality,
            "state": Alarm.state,
            "tag": Alarm.tag,
            "plant": Alarm.plant,
            "area": Alarm.area,
            "priority": Alarm.priority,
            "source_system": Alarm.source_system,
        }
        column = allowed_fields[field_name]
        value_expr = func.coalesce(cast(column, String), "UNKNOWN").label("value")
        count_expr = func.count(Alarm.id).label("alarm_count")
        stmt = self._apply_filters(
            select(value_expr, count_expr).group_by(value_expr).order_by(count_expr.desc(), value_expr),
            start_time=start_time,
            end_time=end_time,
            criticality=criticality,
            tag=tag,
        )
        if limit is not None:
            stmt = stmt.limit(limit)

        rows = self._session.execute(stmt).all()
        return [{"value": str(row.value), "alarm_count": int(row.alarm_count)} for row in rows]
