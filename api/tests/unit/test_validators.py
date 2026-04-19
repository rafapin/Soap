from datetime import datetime
import pytest
from pydantic import ValidationError

from app.schemas.alarm_filters import AlarmFilters


class TestAlarmFilters:
    def test_valid_filters(self):
        filters = AlarmFilters(
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 1, 2),
            criticality="HIGH",
            page=2,
            page_size=50,
        )
        assert filters.criticality == "HIGH"
        assert filters.page == 2

    def test_criticality_case_insensitivity(self):
        filters = AlarmFilters(criticality="high")
        assert filters.criticality == "HIGH"

    def test_invalid_criticality_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            AlarmFilters(criticality="UNKNOWN")
        assert "criticality must be one of" in str(exc_info.value)

    def test_start_after_end_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            AlarmFilters(
                start_time=datetime(2024, 1, 2),
                end_time=datetime(2024, 1, 1),
            )
        assert "start_time must be before or equal to end_time" in str(exc_info.value)

    def test_page_out_of_bounds(self):
        with pytest.raises(ValidationError):
            AlarmFilters(page=0)
        
    def test_page_size_out_of_bounds(self):
        with pytest.raises(ValidationError):
            AlarmFilters(page_size=0)
        with pytest.raises(ValidationError):
            AlarmFilters(page_size=1000)  # Assuming max is 100 or less as per settings
