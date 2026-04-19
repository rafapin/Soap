from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlarmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_alarm_id: Optional[str] = None
    source_system: Optional[str] = None
    tag: str
    message: Optional[str] = None
    priority: Optional[int] = None
    criticality: str
    state: Optional[str] = None
    plant: Optional[str] = None
    area: Optional[str] = None
    equipment: Optional[str] = None
    event_time: datetime
    ack_time: Optional[datetime] = None
    clear_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
