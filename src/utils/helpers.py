# src/utils/helpers.py

import os
from datetime import datetime, date
from typing import Optional, Union

# ============================================
# DATABASE CONFIGURATION
# ============================================


def get_db_path() -> str:
    """
    Get the database file path.

    Returns:
        Path to the SQLite database file

    Example:
        >>> get_db_path()
        'data/habits.db'
    """
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    return os.path.join(data_dir, "habits.db")


# ============================================
# DATE/TIME UTILITIES
# ============================================


def to_iso(dt: Union[datetime, date, str, None]) -> Optional[str]:
    """
    Convert datetime to ISO format string.

    Args:
        dt: datetime object, date object, ISO string, or None

    Returns:
        ISO format string or None if input is None

    Example:
        >>> to_iso(datetime(2024, 1, 1))
        '2024-01-01T00:00:00'
    """
    if dt is None:
        return None

    if isinstance(dt, str):
        return dt

    if isinstance(dt, datetime):
        return dt.isoformat()

    if isinstance(dt, date):
        return datetime.combine(dt, datetime.min.time()).isoformat()

    # noinspection PyBroadException
    try:
        return str(dt)
    except:
        return None


def from_iso(iso_string: Optional[str]) -> Optional[datetime]:
    """
    Convert ISO format string to datetime.

    Args:
        iso_string: ISO format string or None

    Returns:
        datetime object or None if input is None or invalid

    Example:
        >>> from_iso('2024-01-01T00:00:00')
        datetime(2024, 1, 1, 0, 0)
    """
    if iso_string is None:
        return None

    if isinstance(iso_string, datetime):
        return iso_string

    if isinstance(iso_string, str):
        # Skip UUIDs (36 chars with 4 hyphens)
        if len(iso_string) == 36 and iso_string.count("-") == 4:
            return None

        # Skip strings that don't look like dates
        if not any(c in iso_string for c in "-:T"):
            return None

        try:
            return datetime.fromisoformat(iso_string)
        except ValueError:
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(iso_string, fmt)
                except ValueError:
                    continue
            return None

    return None


def parse_datetime(value: Union[str, datetime, date, None]) -> Optional[datetime]:
    """
    Parse various datetime formats.

    Args:
        value: datetime object, date object, ISO string, or None

    Returns:
        datetime object or None if input is None

    Example:
        >>> parse_datetime('2024-01-01')
        datetime(2024, 1, 1, 0, 0)
        >>> parse_datetime(date(2024, 1, 1))
        datetime(2024, 1, 1, 0, 0)
    """
    if value is None:
        return None

    # ✅ Handle datetime objects
    if isinstance(value, datetime):
        return value

    # ✅ Handle date objects (convert to datetime at midnight)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    # Handle strings
    if isinstance(value, str):
        return from_iso(value)

    return None


def format_date_for_display(dt: Union[datetime, str, None]) -> str:
    """
    Format a date for display in the CLI.

    Args:
        dt: datetime object, ISO string, or None

    Returns:
        Formatted date string or 'N/A' if None

    Example:
        >>> format_date_for_display(datetime(2024, 1, 1))
        '2024-01-01'
    """
    if dt is None:
        return "N/A"

    if isinstance(dt, str):
        dt = from_iso(dt)
        if dt is None:
            return "N/A"

    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")

    return str(dt)


def is_valid_date_string(value: str) -> bool:
    """
    Check if a string looks like a valid date.

    Args:
        value: String to check

    Returns:
        True if it looks like a date, False otherwise

    Example:
        >>> is_valid_date_string('2024-01-01')
        True
        >>> is_valid_date_string('abc-123-def')
        False
    """
    if not isinstance(value, str):
        return False

    # Check if it has date separators
    if not any(c in value for c in "-:T"):
        return False

    # Skip UUIDs
    if len(value) == 36 and value.count("-") == 4:
        return False

    return True
