from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.core.config import settings
from app.core.constants import VALID_CRITICALITIES


class AlarmFilters(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    criticality: Optional[str] = Field(default=None, max_length=20)
    tag: Optional[str] = Field(default=None, max_length=200)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=settings.default_page_size, ge=1, le=settings.max_page_size)

    @model_validator(mode="after")
    def validate_time_range(self) -> "AlarmFilters":
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValueError("start_time must be before or equal to end_time")
        return self

    @model_validator(mode="after")
    def validate_criticality_value(self) -> "AlarmFilters":
        if self.criticality and self.criticality.upper() not in VALID_CRITICALITIES:
            raise ValueError(
                f"criticality must be one of: {', '.join(sorted(VALID_CRITICALITIES))}"
            )
        if self.criticality:
            self.criticality = self.criticality.upper()
        return self
