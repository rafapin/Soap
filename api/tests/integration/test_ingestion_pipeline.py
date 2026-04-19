import json
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.alarm import Alarm
from app.db.models.alarm_rejection import AlarmRejection
from app.db.models.ingestion_batch import IngestionBatch
from app.services.ingestion_service import run_ingestion


@pytest.fixture
def sample_dataset_path(tmp_path: Path) -> Path:
    # 2 valid rows, 1 duplicate, 1 missing tag, 1 invalid date
    data = [
        {
            "external_alarm_id": "ALM-1",
            "tag": "TAG_A",
            "criticality": "HIGH",
            "event_time": "2024-01-01T10:00:00",
            "state": "ACTIVE"
        },
        {
            "external_alarm_id": "ALM-2",
            "tag": "TAG_B",
            "criticality": "MEDIUM",
            "event_time": "2024-01-01T10:05:00",
            "state": "ACTIVE"
        },
        {
            "external_alarm_id": "ALM-1",  # duplicate of ALM-1
            "tag": "TAG_A",
            "criticality": "HIGH",
            "event_time": "2024-01-01T10:00:00",
            "state": "ACTIVE"
        },
        {
            "external_alarm_id": "ALM-3",
            "tag": "",  # invalid: missing tag
            "criticality": "LOW",
            "event_time": "2024-01-01T10:10:00",
            "state": "ACTIVE"
        },
        {
            "external_alarm_id": "ALM-4",
            "tag": "TAG_C",
            "criticality": "LOW",
            "event_time": "invalid_date",  # invalid: unparseable date
            "state": "ACTIVE"
        }
    ]
    file_path = tmp_path / "test_dataset.json"
    file_path.write_text(json.dumps(data))
    return file_path


def test_ingestion_pipeline(clean_db: Session, sample_dataset_path: Path):
    summary = run_ingestion(clean_db, sample_dataset_path)

    assert summary["total_rows"] == 5
    assert summary["inserted_rows"] == 2
    assert summary["rejected_rows"] == 3
    assert summary["status"] == "COMPLETED"

    # Verify db state
    batch = clean_db.scalars(select(IngestionBatch)).first()
    assert batch is not None
    assert batch.total_rows == 5
    assert batch.inserted_rows == 2
    assert batch.rejected_rows == 3

    alarms = clean_db.scalars(select(Alarm)).all()
    assert len(alarms) == 2
    assert {a.external_alarm_id for a in alarms} == {"ALM-1", "ALM-2"}

    rejections = clean_db.scalars(select(AlarmRejection)).all()
    assert len(rejections) == 3
    rejection_reasons = " ".join([r.rejection_reason for r in rejections])
    assert "Duplicate record" in rejection_reasons
    assert "tag is required" in rejection_reasons
    assert "event_time is required" in rejection_reasons
