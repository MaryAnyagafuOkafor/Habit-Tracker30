# tests/unit/analytics/test_streak.py

"""
Unit tests for streak analytics functions (Critical Tests Only).
"""

from datetime import datetime, timedelta

from src.analytics.streak import StreakAnalyzer
from src.core.models.habit import Habit


class TestCalculateCurrentStreak:
    """Tests for calculate_current_streak function."""

    def test_calculate_current_streak(self):
        """Test current streak calculation."""
        analyzer = StreakAnalyzer()
        habit = Habit("Exercise", "user_1", periodicity="daily")
        today = datetime.now()

        # 5-day streak
        for i in range(5):
            habit.complete(today - timedelta(days=i))

        assert analyzer.calculate_current_streak(habit) == 5

    def test_calculate_current_streak_broken(self):
        """Test current streak with broken streak."""
        analyzer = StreakAnalyzer()
        habit = Habit("Exercise", "user_1", periodicity="daily")
        today = datetime.now()

        # Complete days 0, 1, 2 (3-day streak)
        # Miss day 3
        # Complete days 4, 5 (older)
        for i in [0, 1, 2, 4, 5]:
            habit.complete(today - timedelta(days=i))

        # Current streak should be 3 (days 0, 1, 2)
        assert analyzer.calculate_current_streak(habit) == 3


class TestCalculateLongestStreak:
    """Tests for calculate_longest_streak function."""

    def test_calculate_longest_streak(self):
        """Test longest streak calculation with gaps."""
        analyzer = StreakAnalyzer()
        habit = Habit("Exercise", "user_1", periodicity="daily")
        today = datetime.now()

        # 5-day streak (days 5-9)
        for i in range(5, 10):
            habit.complete(today - timedelta(days=i))

        # 3-day streak (days 0-2)
        for i in range(3):
            habit.complete(today - timedelta(days=i))

        assert analyzer.calculate_longest_streak(habit) == 5


class TestGetStreakInfo:
    """Tests for get_streak_info function."""

    def test_get_streak_info(self):
        """Test comprehensive streak info."""
        analyzer = StreakAnalyzer()
        habit = Habit("Exercise", "user_1", periodicity="daily")
        today = datetime.now()

        # Add completions for 30 consecutive days including today
        # This ensures the streak counts from today backwards
        for i in range(30):
            habit.complete(today - timedelta(days=i))

        # Also explicitly add today's completion to be safe
        habit.complete(today)

        info = analyzer.get_streak_info(habit)

        assert info["current"] == 30  # or at least 28
        assert info["periodicity"] == "daily"
        assert info["target"] == 28
        assert info["status"] == "✅ COMPLETE"

    def test_get_streak_info_weekly(self):
        """Test streak info for weekly habit."""
        analyzer = StreakAnalyzer()
        habit = Habit("Weekly Review", "user_1", periodicity="weekly")
        today = datetime.now()

        # Add completions for 4 consecutive weeks
        for i in range(4):
            habit.complete(today - timedelta(weeks=i))

        info = analyzer.get_streak_info(habit)

        assert info["current"] == 4
        assert info["periodicity"] == "weekly"
        assert info["target"] == 4
        assert info["status"] == "✅ COMPLETE"

    def test_get_streak_info_monthly(self):
        """Test streak info for monthly habit."""
        analyzer = StreakAnalyzer()
        habit = Habit("Monthly Check", "user_1", periodicity="monthly")
        today = datetime.now()

        # Add completions for 4 consecutive months
        for i in range(4):
            habit.complete(today - timedelta(days=30 * i))

        info = analyzer.get_streak_info(habit)

        assert info["current"] == 4
        assert info["periodicity"] == "monthly"
        assert info["target"] == 4
        assert info["status"] == "✅ COMPLETE"


class TestGetHabitWithLongestStreak:
    """Tests for get_habit_with_longest_streak function."""

    def test_get_habit_with_longest_streak(self):
        """Test finding habit with longest streak."""
        analyzer = StreakAnalyzer()
        habits = []
        today = datetime.now()

        # Habit 1: 5-day streak
        habit1 = Habit("Exercise", "user_1", periodicity="daily")
        for i in range(5):
            habit1.complete(today - timedelta(days=i))
        habits.append(habit1)

        # Habit 2: 3-day streak
        habit2 = Habit("Reading", "user_1", periodicity="daily")
        for i in range(3):
            habit2.complete(today - timedelta(days=i))
        habits.append(habit2)

        # Habit 3: 2-day streak
        habit3 = Habit("Meditate", "user_1", periodicity="daily")
        for i in range(2):
            habit3.complete(today - timedelta(days=i))
        habits.append(habit3)

        result = analyzer.get_habit_with_longest_streak(habits)
        assert result is not None
        assert result["habit"].name == "Exercise"
        assert result["streak_info"]["current"] == 5

    def test_get_habit_with_longest_streak_empty(self):
        """Test with empty habit list."""
        analyzer = StreakAnalyzer()
        result = analyzer.get_habit_with_longest_streak([])
        assert result is None

    def test_get_habit_with_longest_streak_no_completions(self):
        """Test with habits that have no completions."""
        analyzer = StreakAnalyzer()
        habits = [
            Habit("Exercise", "user_1", periodicity="daily"),
            Habit("Reading", "user_1", periodicity="daily"),
        ]
        result = analyzer.get_habit_with_longest_streak(habits)
        # Should return None or first habit with 0 streak
        # Currently returns None if no completions
        assert result is None


class TestGetHabitsByPeriodicity:
    """Tests for get_habits_by_periodicity function."""

    def test_get_habits_by_periodicity_daily(self):
        """Test filtering daily habits."""
        analyzer = StreakAnalyzer()
        habits = []

        habit1 = Habit("Exercise", "user_1", periodicity="daily")
        habit2 = Habit("Reading", "user_1", periodicity="daily")
        habit3 = Habit("Weekly Review", "user_1", periodicity="weekly")
        habit4 = Habit("Monthly Check", "user_1", periodicity="monthly")

        habits.extend([habit1, habit2, habit3, habit4])

        daily = analyzer.get_habits_by_periodicity(habits, "daily")
        assert len(daily) == 2
        for habit in daily:
            assert habit.periodicity == "daily"

    def test_get_habits_by_periodicity_weekly(self):
        """Test filtering weekly habits."""
        analyzer = StreakAnalyzer()
        habits = []

        habit1 = Habit("Exercise", "user_1", periodicity="daily")
        habit2 = Habit("Weekly Review", "user_1", periodicity="weekly")
        habit3 = Habit("Monthly Check", "user_1", periodicity="monthly")

        habits.extend([habit1, habit2, habit3])

        weekly = analyzer.get_habits_by_periodicity(habits, "weekly")
        assert len(weekly) == 1
        assert weekly[0].periodicity == "weekly"

    def test_get_habits_by_periodicity_monthly(self):
        """Test filtering monthly habits."""
        analyzer = StreakAnalyzer()
        habits = []

        habit1 = Habit("Exercise", "user_1", periodicity="daily")
        habit2 = Habit("Weekly Review", "user_1", periodicity="weekly")
        habit3 = Habit("Monthly Check", "user_1", periodicity="monthly")

        habits.extend([habit1, habit2, habit3])

        monthly = analyzer.get_habits_by_periodicity(habits, "monthly")
        assert len(monthly) == 1
        assert monthly[0].periodicity == "monthly"

    def test_get_habits_by_periodicity_invalid(self):
        """Test with invalid periodicity."""
        analyzer = StreakAnalyzer()
        habits = [Habit("Exercise", "user_1", periodicity="daily")]

        try:
            analyzer.get_habits_by_periodicity(habits, "invalid")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert str(e) == "Invalid periodicity: invalid"
