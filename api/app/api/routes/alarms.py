from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.exceptions import AlarmNotFoundError
from app.schemas.alarm_filters import AlarmFilters
from app.schemas.alarm_response import AlarmResponse
from app.schemas.common import PaginatedResponse
from app.services.alarm_query_service import AlarmQueryService

router = APIRouter(prefix="/api/v1/alarms", tags=["Alarms"])


@router.get("", response_model=PaginatedResponse[AlarmResponse], summary="List alarms with filters")
def list_alarms(
    start_time: Optional[datetime] = Query(default=None, description="Filter from this timestamp (inclusive)"),
    end_time: Optional[datetime] = Query(default=None, description="Filter until this timestamp (inclusive)"),
    criticality: Optional[str] = Query(default=None, description="Filter by criticality (HIGH, MEDIUM, LOW)"),
    tag: Optional[str] = Query(default=None, max_length=200, description="Partial match on tag"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        default=settings.default_page_size, ge=1, le=settings.max_page_size, description="Items per page"
    ),
    db: Session = Depends(get_db),
):
    filters = AlarmFilters(
        start_time=start_time,
        end_time=end_time,
        criticality=criticality,
        tag=tag,
        page=page,
        page_size=page_size,
    )

    service = AlarmQueryService(db)
    items, total = service.list_alarms(
        start_time=filters.start_time,
        end_time=filters.end_time,
        criticality=filters.criticality,
        tag=filters.tag,
        page=filters.page,
        page_size=filters.page_size,
    )

    pages = math.ceil(total / filters.page_size) if total > 0 else 0
    return PaginatedResponse(
        items=[AlarmResponse.model_validate(a) for a in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        pages=pages,
    )


@router.get("/{alarm_id}", response_model=AlarmResponse, summary="Get alarm by ID")
def get_alarm(alarm_id: int, db: Session = Depends(get_db)):
    service = AlarmQueryService(db)
    try:
        alarm = service.get_alarm(alarm_id)
    except AlarmNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    return AlarmResponse.model_validate(alarm)
