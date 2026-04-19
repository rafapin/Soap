from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.api.dependencies import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("", summary="Health check")
def health_check(db: Session = Depends(get_db)) -> dict:
    """Returns service status and database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "unavailable"
    return {"status": "ok", "db": db_status}
