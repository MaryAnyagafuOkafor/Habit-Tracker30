# tests/unit/utils/test_helpers.py

"""
Unit tests for utility helper functions.
"""

from datetime import datetime, date

from src.utils.helpers import to_iso, parse_datetime


class TestHelpers:
    """Tests for helper utility functions."""

    def test_to_iso_with_datetime(self):
        """Test to_iso with datetime object."""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = to_iso(dt)
        assert result == "2024-01-15T14:30:45"

    def test_to_iso_with_date(self):
        """Test to_iso with date object."""
        d = date(2024, 1, 15)
        result = to_iso(d)
        assert result == "2024-01-15T00:00:00"

    def test_parse_datetime_with_iso_format(self):
        """Test parse_datetime with ISO format."""
        result = parse_datetime("2024-01-15T14:30:45")
        assert result == datetime(2024, 1, 15, 14, 30, 45)

    def test_parse_datetime_with_date_format(self):
        """Test parse_datetime with date format."""
        result = parse_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15, 0, 0, 0)

    def test_parse_datetime_with_iso_with_timezone(self):
        """Test parse_datetime with timezone info."""
        result = parse_datetime("2024-01-15T14:30:45+00:00")
        # Should handle timezone by returning naive datetime
        assert result is not None
