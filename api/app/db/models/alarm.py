from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_alarm_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tag: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    criticality: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[str | None] = mapped_column(String(30), nullable=True)
    plant: Mapped[str | None] = mapped_column(String(100), nullable=True)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    equipment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    event_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ack_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    clear_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("external_alarm_id", "event_time", "tag", name="uq_alarm_business_key"),
        Index("ix_alarms_event_time", "event_time"),
        Index("ix_alarms_criticality", "criticality"),
        Index("ix_alarms_tag", "tag"),
        Index("ix_alarms_criticality_event_time", "criticality", "event_time"),
        Index("ix_alarms_tag_event_time", "tag", "event_time"),
    )
