"""
HABIT MODEL - Business Logic Layer
===================================

This module defines the Habit class for tracking habits with completion logging,
streak tracking, and serialization.

Key Features:
    - Event logging (all completion timestamps are stored)
    - Period-based checking (daily, weekly, monthly)
    - Serialization to/from dictionary for database storage
    - Streak methods delegated to streak analytics (single source of truth)

Example:
    >>> habit = Habit("Exercise", "user_1", "Daily exercise", "daily")
    >>> habit.complete()
    >>> habit.get_current_streak()
    1
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from src.utils.helpers import parse_datetime, to_iso


class Habit:
    """
    Habit Model with Event Log.

    Represents a habit that a user wants to track. All completion events
    are stored as timestamps in an event log.

    Attributes:
        habit_id (str): Unique identifier (UUID v4)
        user_id (str): ID of the user who owns this habit
        name (str): Habit name
        description (str): Optional description
        periodicity (str): 'daily', 'weekly', or 'monthly'
        created_at (datetime): When the habit was created
        completions (List[datetime]): All completion timestamps
        is_active (bool): Whether the habit is active
    """

    # Class-level StreakAnalyzer instance (shared across all Habit instances)
    _analyzer = None

    # ============================================
    # INITIALIZATION
    # ============================================

    def __init__(
        self,
        name: str,
        user_id: str,
        description: str = "",
        periodicity: str = "daily",
        habit_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        completions: Optional[List[datetime]] = None,
        is_active: bool = True,
    ):
        """
        Initialize a new Habit instance.

        Args:
            name: The name of the habit
            user_id: ID of the user who owns this habit
            description: Optional description
            periodicity: 'daily', 'weekly', or 'monthly'
            habit_id: Optional UUID (auto-generated if not provided)
            created_at: Creation timestamp (defaults to now)
            completions: List of completion timestamps
            is_active: Whether the habit is active
        """
        self.habit_id = habit_id if habit_id else str(uuid.uuid4())
        self.user_id = user_id
        self.name = name
        self.description = description if description else ""
        self.periodicity = periodicity.lower() if periodicity else "daily"
        self.created_at = created_at if created_at else datetime.now()
        self.completions: List[datetime] = completions if completions else []
        self.is_active = is_active

    @classmethod
    def _get_analyzer(cls):
        """
        Get or create the shared StreakAnalyzer instance.

        Returns:
            StreakAnalyzer: The shared analyzer instance
        """
        if cls._analyzer is None:
            from src.analytics.streak import StreakAnalyzer

            cls._analyzer = StreakAnalyzer()
        return cls._analyzer

    # ============================================
    # COMPLETION MANAGEMENT
    # ============================================

    def complete(self, completion_time: Optional[datetime] = None) -> None:
        """
        Add a completion timestamp to the event log.

        Args:
            completion_time: Optional datetime. Defaults to now.
        """
        if self.completions is None:
            self.completions = []

        # Clean any None values
        self.completions = [c for c in self.completions if c is not None]

        # Convert string completions to datetime (for safety)
        converted = []
        for c in self.completions:
            if isinstance(c, datetime):
                converted.append(c)
            elif isinstance(c, str):
                dt = parse_datetime(c)
                if dt:
                    converted.append(dt)
        self.completions = converted

        # Add the new completion
        if completion_time is None:
            self.completions.append(datetime.now())
        elif isinstance(completion_time, datetime):
            self.completions.append(completion_time)
        else:
            dt = parse_datetime(completion_time)
            if dt:
                self.completions.append(dt)

        # Sort chronologically
        self.completions.sort()

    def add_completion(self, completion_time: Optional[datetime] = None) -> None:
        """
        Alias for complete() for compatibility.

        Args:
            completion_time: Optional datetime. Defaults to now.
        """
        self.complete(completion_time)

    def add_completions(self, completion_times: List[datetime]) -> None:
        """
        Add multiple completion timestamps at once.

        Args:
            completion_times: List of datetime objects to add
        """
        for dt in completion_times:
            self.complete(dt)

    # ============================================
    # PERIOD HELPER METHODS
    # ============================================

    def get_period_days(self) -> int:
        """
        Get the number of days in one period for this habit.

        Returns:
            int: 1 for daily, 7 for weekly, 30 for monthly

        Example:
            >>> Habit("Exercise", "user_1", periodicity="daily").get_period_days()
            1
            >>> Habit("Exercise", "user_1", periodicity="weekly").get_period_days()
            7
        """
        periodicity = self.periodicity.lower()
        if periodicity == "daily":
            return 1
        elif periodicity == "weekly":
            return 7
        elif periodicity == "monthly":
            return 30
        return 1

    def get_period_start(self, date: datetime) -> datetime:
        """
        Get the start date of the period containing the given date.

        For daily: returns midnight of the same day.
        For weekly: returns Monday midnight.
        For monthly: returns 1st of the month at midnight.

        Args:
            date: The date to calculate the period start for

        Returns:
            datetime: Start of the period at midnight

        """
        period_days = self.get_period_days()

        if period_days == 1:
            # Daily: start at midnight
            return datetime(date.year, date.month, date.day)
        elif period_days == 7:
            # Weekly: start on Monday
            days_since_monday = date.weekday()
            period_start = date - timedelta(days=days_since_monday)
            return datetime(period_start.year, period_start.month, period_start.day)
        else:
            # Monthly: start on the 1st
            return datetime(date.year, date.month, 1)

    def was_completed_in_period(self, period_start: datetime) -> bool:
        """
        Check if there was a completion in the given period.

        Args:
            period_start: Start of the period

        Returns:
            bool: True if a completion exists in this period

        Example:
            >>> habit = Habit("Exercise", "user_1", periodicity="daily")
            >>> habit.complete(datetime(2024, 6, 15, 10, 0, 0))
            >>> habit.was_completed_in_period(datetime(2024, 6, 15, 0, 0, 0))
            True
        """
        period_days = self.get_period_days()
        period_end = period_start + timedelta(days=period_days)

        for completion in self.completions:
            if period_start <= completion <= period_end:
                return True
        return False

    def is_broken(self, check_date: Optional[datetime] = None) -> bool:
        """
        Check if the habit is currently broken (no completion in the current period).

        Args:
            check_date: Date to check (defaults to now)

        Returns:
            bool: True if the habit is broken (no completion in the current period)
        """
        if check_date is None:
            check_date = datetime.now()

        period_start = self.get_period_start(check_date)
        return not self.was_completed_in_period(period_start)

    # ============================================
    # STREAK METHODS (DELEGATE TO ANALYTICS)
    # ============================================

    def get_current_streak(self) -> int:
        """
        Get the current streak count.

        Delegates to StreakAnalyzer.calculate_current_streak()

        Returns:
            int: Current streak count
        """
        return self._get_analyzer().calculate_current_streak(self)

    def get_longest_streak(self) -> int:
        """
        Get the longest streak achieved.

        Delegates to StreakAnalyzer.calculate_longest_streak()

        Returns:
            int: Longest streak count
        """
        return self._get_analyzer().calculate_longest_streak(self)

    def get_streak_info(self) -> dict:
        """
        Get comprehensive streak information.

        Delegates to StreakAnalyzer.get_streak_info()

        Returns:
            dict: Complete streak information
        """
        return self._get_analyzer().get_streak_info(self)

    def get_streak_display(self) -> str:
        """
        Get a formatted streak display string.

        Returns:
            str: Formatted streak string (e.g., "5 / 28 days")
        """
        info = self.get_streak_info()
        return f"{info['current']} / {info['target']} {info['unit_plural']}"

    def is_streak_complete(self) -> bool:
        """
        Check if the habit has reached its streak target.

        Returns:
            bool: True if the streak target is complete
        """
        return self.get_streak_info()["is_complete"]

    def get_streak_status(self) -> str:
        """
        Get the streak status: COMPLETE, IN PROGRESS, or NOT STARTED.

        Returns:
            str: Status string
        """
        return self.get_streak_info()["status"]

    # ============================================
    # SERIALIZATION
    # ============================================

    def to_dict(self) -> dict:
        """
        Serialize the habit to a dictionary for database storage.

        Returns:
            dict: Dictionary representation of the habit

        Example:
            >>> habit = Habit("Exercise", "user_1")
            >>> habit.to_dict()
            {'habit_id': '...', 'name': 'Exercise', ...}
        """
        return {
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "periodicity": self.periodicity,
            "created_at": to_iso(self.created_at),
            "completions": [to_iso(c) for c in self.completions if c is not None],
            "is_active": 1 if self.is_active else 0,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Habit":
        """
        Create a Habit instance from a dictionary (database record).

        Args:
            data: Dictionary containing habit data

        Returns:
            Habit: New Habit instance

        """
        # Convert completion timestamps from ISO format
        completions = []
        for c in data.get("completions", []):
            if c is not None:
                dt = parse_datetime(c)
                if dt:
                    completions.append(dt)

        # Convert created_at from ISO format
        created_at = parse_datetime(data.get("created_at"))

        return cls(
            name=data["name"],
            user_id=data["user_id"],
            description=data.get("description", ""),
            periodicity=data.get("periodicity", "daily"),
            habit_id=data.get("habit_id", str(uuid.uuid4())),
            created_at=created_at if created_at else datetime.now(),
            completions=completions,
            is_active=bool(data.get("is_active", True)),
        )

    # ============================================
    # STRING REPRESENTATION
    # ============================================

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Habit: {self.name} (ID: {self.habit_id})"

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"Habit(habit_id='{self.habit_id}', "
            f"name='{self.name}', "
            f"periodicity='{self.periodicity}')"
        )
