# src/analytics/streak.py

"""
HABIT ANALYTICS - Streak Calculation Module
============================================

This module provides a class-based approach for calculating and analyzing habit streaks.

Key Features:
    - Current streak calculation (consecutive periods from today)
    - Longest streak calculation (best performance ever)
    - Periodicity filtering (daily/weekly/monthly)
    - Progress tracking with visual indicators
    - Milestone messages for motivation
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from src.core.models.habit import Habit


class StreakAnalyzer:
    """
    A class for analyzing habit streaks using functional programming principles.

    This class provides pure methods for streak calculation and analysis.
    All methods are side-effect free and operate on data structures.
    """

    # ============================================================
    # PERIOD KEY HELPERS
    # ============================================================

    @staticmethod
    def _get_period_key(dt: datetime, periodicity: str) -> Union[date, Tuple[int, int]]:
        """
        Convert a datetime to a period key based on the periodicity.

        A period key is a simplified representation of a time period:
            - Daily: date object (e.g., 2024-01-15)
            - Weekly: (year, week_number) tuple (e.g., (2024, 3))
            - Monthly: (year, month) tuple (e.g., (2024, 1))

        Args:
            dt: The datetime to convert
            periodicity: 'daily', 'weekly', or 'monthly'

        Returns:
            The period key (date, tuple, or other comparable type)
        """
        periodicity = periodicity.lower()

        if periodicity == "daily":
            return dt.date()
        elif periodicity == "weekly":
            year, week, _ = dt.isocalendar()
            return year, week
        elif periodicity == "monthly":
            return dt.year, dt.month
        else:
            return dt.date()

    @staticmethod
    def _get_unique_periods(dates: List[datetime], periodicity: str) -> Set:
        """
        Extract unique periods from a list of completion dates.

        Args:
            dates: List of datetime objects
            periodicity: 'daily', 'weekly', or 'monthly'

        Returns:
            Set of unique period keys
        """
        periods = set()
        for dt in dates:
            period_key = StreakAnalyzer._get_period_key(dt, periodicity)
            periods.add(period_key)
        return periods

    @staticmethod
    def _is_consecutive(prev_period, curr_period, periodicity: str) -> bool:
        """
        Check if two periods are consecutive (no gap between them).

        Args:
            prev_period: The earlier period key
            curr_period: The later period key
            periodicity: 'daily', 'weekly', or 'monthly'

        Returns:
            True if the periods are consecutive, False otherwise
        """
        periodicity = periodicity.lower()

        if periodicity == "daily":
            return (curr_period - prev_period).days == 1

        elif periodicity == "weekly":
            prev_year, prev_week = prev_period
            curr_year, curr_week = curr_period

            if prev_year == curr_year:
                return curr_week - prev_week == 1
            else:
                prev_date = datetime(prev_year, 12, 31)
                curr_date = datetime(curr_year, 1, 1)
                weeks_between = (curr_date - prev_date).days // 7
                return curr_week + weeks_between - prev_week == 1

        elif periodicity == "monthly":
            prev_year, prev_month = prev_period
            curr_year, curr_month = curr_period
            month_diff = (curr_year - prev_year) * 12 + (curr_month - prev_month)
            return month_diff == 1

        return False

    # ============================================================
    # STREAK CALCULATION METHODS
    # ============================================================

    def calculate_current_streak(self, habit: Habit) -> int:
        """
        Calculate the current streak for a habit.

        A streak is the number of consecutive periods (days/weeks/months)
        that the habit has been completed. The streak starts from today
        and counts backwards until a gap is found.

        Args:
            habit: Habit object with completions and periodicity

        Returns:
            int: Current streak count (0 if no completions or broken)
        """
        if not habit.completions:
            return 0

        dates = [c for c in habit.completions if isinstance(c, datetime)]
        if not dates:
            return 0

        periodicity = habit.periodicity.lower()

        periods = self._get_unique_periods(dates, periodicity)
        if not periods:
            return 0

        today = datetime.now()
        today_period = self._get_period_key(today, periodicity)

        # Determine starting period
        if periodicity == "daily":
            if today_period in periods:
                start_period = today_period
            else:
                yesterday = today - timedelta(days=1)
                yesterday_period = self._get_period_key(yesterday, periodicity)
                if yesterday_period in periods:
                    start_period = yesterday_period
                else:
                    return 0
        else:
            if today_period not in periods:
                if periodicity == "weekly":
                    year, week = today_period
                    prev_period = (year, week - 1) if week > 1 else (year - 1, 52)
                    if prev_period not in periods:
                        return 0
                    start_period = prev_period
                else:  # monthly
                    year, month = today_period
                    prev_period = (year, month - 1) if month > 1 else (year - 1, 12)
                    if prev_period not in periods:
                        return 0
                    start_period = prev_period
            else:
                start_period = today_period

        # Count consecutive periods backwards
        streak = 0
        current_period = start_period
        periods_set = set(periods)

        while True:
            if current_period in periods_set:
                streak += 1
                if periodicity == "daily":
                    if isinstance(current_period, date):
                        current_period = current_period - timedelta(days=1)
                    else:
                        break
                elif periodicity == "weekly":
                    year, week = current_period
                    current_period = (year, week - 1) if week > 1 else (year - 1, 52)
                elif periodicity == "monthly":
                    year, month = current_period
                    current_period = (year, month - 1) if month > 1 else (year - 1, 12)
                else:
                    break
            else:
                break

        return streak

    def calculate_longest_streak(self, habit: Habit) -> int:
        """
        Calculate the longest (best) streak ever achieved for a habit.

        Args:
            habit: Habit object with completions and periodicity

        Returns:
            int: Longest streak count (0 if no completions)
        """
        if not habit.completions:
            return 0

        dates = [c for c in habit.completions if isinstance(c, datetime)]
        if not dates:
            return 0

        periodicity = habit.periodicity.lower()
        periods = self._get_unique_periods(dates, periodicity)
        if not periods:
            return 0

        sorted_periods = sorted(periods)

        if len(sorted_periods) == 1:
            return 1

        longest_streak = 1
        current_streak = 1

        for i in range(1, len(sorted_periods)):
            prev_period = sorted_periods[i - 1]
            curr_period = sorted_periods[i]

            if self._is_consecutive(prev_period, curr_period, periodicity):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return longest_streak

    def get_streak_info(self, habit: Habit) -> Dict[str, Any]:
        """
        Get comprehensive streak information for a habit.

        Args:
            habit: Habit object with completions and periodicity

        Returns:
            dict: Complete streak information
        """
        current = self.calculate_current_streak(habit)
        longest = self.calculate_longest_streak(habit)
        total_completions = len(habit.completions)

        periodicity = habit.periodicity.lower()
        if periodicity == "daily":
            target = 28
            unit = "day"
            unit_plural = "days"
            label = "Daily"
        elif periodicity == "weekly":
            target = 4
            unit = "week"
            unit_plural = "weeks"
            label = "Weekly"
        elif periodicity == "monthly":
            target = 4
            unit = "month"
            unit_plural = "months"
            label = "Monthly"
        else:
            target = 4
            unit = "period"
            unit_plural = "periods"
            label = "Unknown"

        progress = min((current / target) * 100, 100) if target > 0 else 0

        if current >= target:
            status = "✅ COMPLETE"
            is_complete = True
        elif current > 0:
            status = "🔄 IN PROGRESS"
            is_complete = False
        else:
            status = "⏳ NOT STARTED"
            is_complete = False

        milestone_msg = self._get_milestone_message(current, periodicity)

        return {
            "habit_id": habit.habit_id,
            "name": habit.name,
            "periodicity": periodicity,
            "period_label": label,
            "current": current,
            "longest": longest,
            "target": target,
            "progress": progress,
            "progress_display": f"{progress:.0f}%",
            "current_display": f"{current} {unit_plural if current != 1 else unit}",
            "longest_display": f"{longest} {unit_plural if longest != 1 else unit}",
            "target_display": f"{target} {unit_plural}",
            "unit": unit,
            "unit_plural": unit_plural,
            "status": status,
            "is_complete": is_complete,
            "total_completions": total_completions,
            "milestone_msg": milestone_msg,
        }

    @staticmethod
    def _get_milestone_message(streak: int, periodicity: str) -> Optional[str]:
        """Generate motivational milestone message based on streak length."""
        if streak == 0:
            return None

        if periodicity == "daily":
            if streak >= 28:
                return "🎉🏆 INCREDIBLE! Full 28-day streak! 💪🌟"
            elif streak >= 14:
                return "🎉 Amazing! 14-day streak! Halfway to 28! 💪"
            elif streak >= 7:
                return "💪 Great start! 1-week streak! 🔥"
            elif streak >= 3:
                return "📈 Building momentum! Keep going! 💪"
            else:
                return "🌱 Great beginning! Keep showing up! ⭐"

        elif periodicity == "weekly":
            if streak >= 4:
                return "🎉🏆 OUTSTANDING! Full 4-week streak! 🌟💪"
            elif streak >= 2:
                return "🎉 Great job! 2-week streak! Halfway to 4! 💪"
            else:
                return "🌟 Excellent start! Week by week! 💪"

        else:  # monthly
            if streak >= 4:
                return "🎉🏆 LEGENDARY! Full 4-month streak! 🌟💪"
            elif streak >= 3:
                return "🎉 Amazing! 3-month streak! One more to go! 🔥"
            elif streak >= 2:
                return "🎉 Great job! 2-month streak! Halfway there! 💪"
            else:
                return "🎉 Excellent! First month complete! 🌟"

    def get_habit_with_longest_streak(
        self, habits: List[Habit]
    ) -> Optional[Dict[str, Any]]:
        """
        Find the habit with the longest streak among a list of habits.
        """
        if not habits:
            return None

        best_habit = None
        best_streak_in_days = 0  # ✅ Start at 0 (only accept streaks > 0)
        best_info = None

        for habit in habits:
            info = self.get_streak_info(habit)
            periodicity = habit.periodicity.lower()
            current_streak = info["current"]

            # Skip habits with no streak
            if current_streak == 0:  # ✅ Skip if no streak
                continue

            # Convert to days for comparison
            if periodicity == "daily":
                streak_in_days = current_streak
            elif periodicity == "weekly":
                streak_in_days = current_streak * 7
            elif periodicity == "monthly":
                streak_in_days = current_streak * 30
            else:
                streak_in_days = current_streak

            if streak_in_days > best_streak_in_days:
                best_streak_in_days = streak_in_days
                best_habit = habit
                best_info = info

        # ✅ Only return if we found a habit with a streak > 0
        if best_habit and best_streak_in_days > 0:
            return {"habit": best_habit, "streak_info": best_info}
        return None

    @staticmethod
    def create_progress_bar(progress: float, length: int = 20) -> str:
        """
        Create a visual progress bar for displaying in the CLI.

        Args:
            progress: Progress percentage (0-100)
            length: Total length of the bar in characters

        Returns:
            Progress bar string with percentage
        """
        if progress < 0:
            progress = 0
        elif progress > 100:
            progress = 100

        filled = int((progress / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {progress:.0f}%"

    @staticmethod
    def display_full_dashboard() -> None:
        """Display a complete dashboard with all streak information."""
        pass

    @staticmethod
    def get_habits_by_periodicity(habits: List[Habit], periodicity: str) -> List[Habit]:
        """
        Filter a list of habits by periodicity.

        Args:
            habits: List of habit objects
            periodicity: 'daily', 'weekly', or 'monthly'

        Returns:
            List of habits with the specified periodicity
        """
        periodicity = periodicity.lower()
        valid = {"daily", "weekly", "monthly"}
        if periodicity not in valid:
            raise ValueError(f"Invalid periodicity: {periodicity}")
        return [habit for habit in habits if habit.periodicity.lower() == periodicity]
