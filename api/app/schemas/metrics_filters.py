from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.core.constants import MAX_TOP_TAGS_LIMIT, VALID_CRITICALITIES


class MetricsSummaryFilters(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tag: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def validate_time_range(self) -> "MetricsSummaryFilters":
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValueError("start_time must be before or equal to end_time")
        return self


class ChartsMetricsFilters(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    criticality: Optional[str] = Field(default=None, max_length=20)
    tag: Optional[str] = Field(default=None, max_length=200)
    bucket: str = Field(default="day")
    limit: int = Field(default=10, ge=1, le=MAX_TOP_TAGS_LIMIT)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ChartsMetricsFilters":
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValueError("start_time must be before or equal to end_time")
        return self

    @model_validator(mode="after")
    def validate_criticality_value(self) -> "ChartsMetricsFilters":
        if self.criticality and self.criticality.upper() not in VALID_CRITICALITIES:
            raise ValueError(f"criticality must be one of: {', '.join(sorted(VALID_CRITICALITIES))}")
        if self.criticality:
            self.criticality = self.criticality.upper()
        return self

    @model_validator(mode="after")
    def validate_bucket(self) -> "ChartsMetricsFilters":
        normalized = self.bucket.lower()
        if normalized not in {"hour", "day"}:
            raise ValueError("bucket must be one of: hour, day")
        self.bucket = normalized
        return self
