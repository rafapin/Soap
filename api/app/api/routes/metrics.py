from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.constants import DEFAULT_TOP_TAGS_LIMIT, MAX_TOP_TAGS_LIMIT
from app.schemas.metric_response import ChartsMetricsResponse, MetricsSummary, TopTagItem, TopTagsResponse
from app.schemas.metrics_filters import ChartsMetricsFilters, MetricsSummaryFilters
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/top-tags", response_model=TopTagsResponse, summary="Top alarm tags by frequency")
def top_tags(
    start_time: Optional[datetime] = Query(default=None, description="Filter from this timestamp"),
    end_time: Optional[datetime] = Query(default=None, description="Filter until this timestamp"),
    limit: int = Query(
        default=DEFAULT_TOP_TAGS_LIMIT,
        ge=1,
        le=MAX_TOP_TAGS_LIMIT,
        description="Maximum number of tags to return",
    ),
    db: Session = Depends(get_db),
):
    service = MetricsService(db)
    results = service.top_tags(start_time=start_time, end_time=end_time, limit=limit)
    return TopTagsResponse(
        items=[TopTagItem(**r) for r in results],
        total_tags=len(results),
    )


@router.get("/charts", response_model=ChartsMetricsResponse, summary="Aggregated chart metrics")
def charts(
    start_time: Optional[datetime] = Query(default=None, description="Filter from this timestamp"),
    end_time: Optional[datetime] = Query(default=None, description="Filter until this timestamp"),
    criticality: Optional[str] = Query(default=None, description="Filter by criticality (HIGH, MEDIUM, LOW)"),
    tag: Optional[str] = Query(default=None, max_length=200, description="Partial match on tag"),
    bucket: str = Query(default="day", description="Timeline bucket: hour or day"),
    limit: int = Query(default=10, ge=1, le=MAX_TOP_TAGS_LIMIT, description="Maximum grouped values to return"),
    db: Session = Depends(get_db),
):
    filters = ChartsMetricsFilters(
        start_time=start_time,
        end_time=end_time,
        criticality=criticality,
        tag=tag,
        bucket=bucket,
        limit=limit,
    )
    service = MetricsService(db)
    return ChartsMetricsResponse(
        **service.charts(
            start_time=filters.start_time,
            end_time=filters.end_time,
            criticality=filters.criticality,
            tag=filters.tag,
            bucket=filters.bucket,
            limit=filters.limit,
        )
    )


@router.get("/summary", response_model=MetricsSummary, summary="Summary metrics for dashboard")
def summary(
    start_time: Optional[datetime] = Query(default=None, description="Filter from this timestamp"),
    end_time: Optional[datetime] = Query(default=None, description="Filter until this timestamp"),
    tag: Optional[str] = Query(default=None, max_length=200, description="Partial match on tag"),
    db: Session = Depends(get_db),
):
    filters = MetricsSummaryFilters(start_time=start_time, end_time=end_time, tag=tag)
    service = MetricsService(db)
    return MetricsSummary(**service.summary(start_time=filters.start_time, end_time=filters.end_time, tag=filters.tag))
