from datetime import datetime, timedelta
import pytest

from app.domain.validators import (
    normalize_criticality,
    normalize_state,
    clean_string,
    validate_temporal_consistency,
)


class TestNormalizeCriticality:
    @pytest.mark.parametrize("raw,expected", [
        ("HIGH", "HIGH"),
        ("High", "HIGH"),
        ("high", "HIGH"),
        ("H", "HIGH"),
        ("MEDIUM", "MEDIUM"),
        ("Medium", "MEDIUM"),
        ("MED", "MEDIUM"),
        ("M", "MEDIUM"),
        ("LOW", "LOW"),
        ("Low", "LOW"),
        ("L", "LOW"),
    ])
    def test_valid_variants(self, raw, expected):
        assert normalize_criticality(raw) == expected

    def test_invalid_returns_none(self):
        assert normalize_criticality("CRITICAL") is None

    def test_unknown_returns_none(self):
        assert normalize_criticality("P1") is None

    def test_none_returns_none(self):
        assert normalize_criticality(None) is None

    def test_empty_returns_none(self):
        assert normalize_criticality("") is None


class TestCleanString:
    def test_strips_leading_trailing(self):
        assert clean_string("  hello  ") == "hello"

    def test_collapses_spaces(self):
        assert clean_string("TAG  A") == "TAG A"

    def test_max_length_truncates(self):
        long = "a" * 300
        result = clean_string(long, max_length=200)
        assert len(result) == 200

    def test_empty_returns_none(self):
        assert clean_string("") is None

    def test_none_returns_none(self):
        assert clean_string(None) is None

    def test_whitespace_only_returns_none(self):
        assert clean_string("   ") is None


class TestValidateTemporalConsistency:
    def test_valid_all_set(self):
        event = datetime(2024, 1, 1, 10, 0)
        ack = event + timedelta(hours=1)
        clear = ack + timedelta(hours=2)
        errors = validate_temporal_consistency(event, ack, clear)
        assert errors == []

    def test_ack_before_event(self):
        event = datetime(2024, 1, 1, 10, 0)
        ack = event - timedelta(hours=1)
        errors = validate_temporal_consistency(event, ack, None)
        assert any("ack_time" in e for e in errors)

    def test_clear_before_event(self):
        event = datetime(2024, 1, 1, 10, 0)
        clear = event - timedelta(hours=1)
        errors = validate_temporal_consistency(event, None, clear)
        assert any("clear_time" in e for e in errors)

    def test_no_event_time(self):
        errors = validate_temporal_consistency(None, None, None)
        assert any("event_time" in e for e in errors)

    def test_optional_fields_none(self):
        event = datetime(2024, 1, 1, 10, 0)
        errors = validate_temporal_consistency(event, None, None)
        assert errors == []
