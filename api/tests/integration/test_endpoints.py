from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.db.models.alarm import Alarm

pytestmark = pytest.mark.asyncio


@pytest.fixture
def test_alarms(clean_db: Session):
    alarms = [
        Alarm(
            external_alarm_id="ALM-001",
            tag="TAG_A",
            criticality="HIGH",
            event_time=datetime(2024, 1, 1, 10, 0),
        ),
        Alarm(
            external_alarm_id="ALM-002",
            tag="TAG_B",
            criticality="MEDIUM",
            event_time=datetime(2024, 1, 2, 10, 0),
        ),
        Alarm(
            external_alarm_id="ALM-003",
            tag="TAG_A",
            criticality="LOW",
            event_time=datetime(2024, 1, 3, 10, 0),
        ),
    ]
    clean_db.add_all(alarms)
    clean_db.commit()
    for a in alarms:
        clean_db.refresh(a)
    return alarms


class TestAlarmsEndpoint:
    async def test_get_alarms_paginated(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/alarms")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

    async def test_filter_by_criticality(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/alarms?criticality=HIGH")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["criticality"] == "HIGH"

    async def test_filter_by_tag(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/alarms?tag=TAG_A")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(i["tag"] == "TAG_A" for i in data["items"])

    async def test_filter_by_time_range(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get(
            "/api/v1/alarms",
            params={"start_time": "2024-01-02T00:00:00", "end_time": "2024-01-03T23:59:59"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_invalid_time_range_returns_422(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get(
            "/api/v1/alarms",
            params={"start_time": "2024-01-03T00:00:00", "end_time": "2024-01-01T00:00:00"},
        )
        assert response.status_code == 422

    async def test_invalid_criticality_returns_422(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/alarms?criticality=UNKNOWN")
        assert response.status_code == 422

    async def test_get_single_alarm(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        alarm_id = test_alarms[0].id
        response = await async_client.get(f"/api/v1/alarms/{alarm_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == alarm_id

    async def test_get_nonexistent_alarm_returns_404(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/alarms/99999")
        assert response.status_code == 404


class TestMetricsEndpoint:
    async def test_top_tags(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/metrics/top-tags")
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_tags"] == 2
        # TAG_A should have 2, TAG_B should have 1
        tags = {item["tag"]: item["alarm_count"] for item in data["items"]}
        assert tags["TAG_A"] == 2
        assert tags["TAG_B"] == 1

    async def test_summary(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/metrics/summary")
        assert response.status_code == 200
        data = response.json()

        assert data["total_alarms"] == 3
        assert data["by_criticality"] == {"HIGH": 1, "LOW": 1, "MEDIUM": 1}
        assert data["by_state"] == {"UNKNOWN": 3}
        assert data["latest_event_time"].startswith("2024-01-03T10:00:00")

    async def test_summary_invalid_time_range_returns_422(self, async_client: AsyncClient):
        response = await async_client.get(
            "/api/v1/metrics/summary",
            params={"start_time": "2024-01-03T00:00:00", "end_time": "2024-01-01T00:00:00"},
        )
        assert response.status_code == 422

    async def test_charts_metrics(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/metrics/charts", params={"bucket": "day", "limit": 5})
        assert response.status_code == 200
        data = response.json()

        assert data["timeline"] == [
            {"period": "2024-01-01", "alarm_count": 1},
            {"period": "2024-01-02", "alarm_count": 1},
            {"period": "2024-01-03", "alarm_count": 1},
        ]
        assert {item["value"]: item["alarm_count"] for item in data["by_criticality"]} == {
            "HIGH": 1,
            "LOW": 1,
            "MEDIUM": 1,
        }
        assert {item["value"]: item["alarm_count"] for item in data["top_tags"]} == {"TAG_A": 2, "TAG_B": 1}
        assert data["by_state"] == [{"value": "UNKNOWN", "alarm_count": 3}]

    async def test_charts_metrics_supports_filters_and_hour_bucket(
        self, async_client: AsyncClient, test_alarms: list[Alarm]
    ):
        response = await async_client.get(
            "/api/v1/metrics/charts",
            params={"criticality": "HIGH", "tag": "TAG_A", "bucket": "hour"},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["timeline"] == [{"period": "2024-01-01 10:00", "alarm_count": 1}]
        assert data["by_criticality"] == [{"value": "HIGH", "alarm_count": 1}]

    async def test_charts_invalid_bucket_returns_422(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/metrics/charts", params={"bucket": "minute"})
        assert response.status_code == 422

    async def test_page_out_of_range_returns_empty_page(self, async_client: AsyncClient, test_alarms: list[Alarm]):
        response = await async_client.get("/api/v1/alarms", params={"page": 99, "page_size": 10})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["items"] == []


class TestHealthEndpoint:
    async def test_health_check(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["db"] == "connected"
