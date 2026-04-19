from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TopTagItem(BaseModel):
    tag: str
    alarm_count: int


class TopTagsResponse(BaseModel):
    items: list[TopTagItem]
    total_tags: int


class MetricsSummary(BaseModel):
    total_alarms: int
    by_criticality: dict[str, int]
    by_state: dict[str, int]
    latest_event_time: datetime | None


class TimelineMetricItem(BaseModel):
    period: str
    alarm_count: int


class ChartMetricItem(BaseModel):
    value: str
    alarm_count: int


class ChartsMetricsResponse(BaseModel):
    timeline: list[TimelineMetricItem]
    by_criticality: list[ChartMetricItem]
    by_state: list[ChartMetricItem]
    top_tags: list[ChartMetricItem]
    by_plant: list[ChartMetricItem]
    by_area: list[ChartMetricItem]
    by_priority: list[ChartMetricItem]
    by_source_system: list[ChartMetricItem]
