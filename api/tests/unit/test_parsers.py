from datetime import datetime, timedelta
import pytest
from app.ingestion.parsers import parse_datetime, parse_priority, parse_string


class TestParseDatetime:
    def test_iso8601_format(self):
        result = parse_datetime("2024-06-01T12:00:00")
        assert result == datetime(2024, 6, 1, 12, 0, 0)

    def test_ddmmyyyy_format(self):
        result = parse_datetime("15/06/2024 08:30:00")
        assert result == datetime(2024, 6, 15, 8, 30, 0)

    def test_mmddyyyy_format(self):
        result = parse_datetime("06/15/2024 08:30:00")
        assert result == datetime(2024, 6, 15, 8, 30, 0)

    def test_iso_with_z(self):
        result = parse_datetime("2024-06-01T12:00:00Z")
        assert result == datetime(2024, 6, 1, 12, 0, 0)

    def test_none_returns_none(self):
        assert parse_datetime(None) is None

    def test_empty_string_returns_none(self):
        assert parse_datetime("") is None

    def test_nan_string_returns_none(self):
        assert parse_datetime("nan") is None

    def test_invalid_date_returns_none(self):
        assert parse_datetime("32/13/2024 99:99:99") is None

    def test_plain_invalid_string_returns_none(self):
        assert parse_datetime("not_a_date") is None

    def test_null_string_returns_none(self):
        assert parse_datetime("null") is None


class TestParsePriority:
    def test_integer_string(self):
        assert parse_priority("3") == 3

    def test_float_string(self):
        assert parse_priority("3.0") == 3

    def test_empty_returns_none(self):
        assert parse_priority("") is None

    def test_text_returns_none(self):
        assert parse_priority("HIGH") is None

    def test_none_returns_none(self):
        assert parse_priority(None) is None


class TestParseString:
    def test_strips_whitespace(self):
        assert parse_string("  TAG_001  ") == "TAG_001"

    def test_empty_returns_none(self):
        assert parse_string("") is None

    def test_none_returns_none(self):
        assert parse_string(None) is None

    def test_nan_returns_none(self):
        assert parse_string("nan") is None
