# tests/unit/analytics/test_heatmap.py

"""
Unit tests for heatmap analytics module.
"""

from datetime import datetime, timedelta

from src.analytics.heatmap import HabitHeatmap
from src.core.models.habit import Habit


class TestHabitHeatmap:
    """Tests for HabitHeatmap class."""

    def test_heatmap_initialization_with_completions(self):
        """Test that HabitHeatmap initializes with existing completions."""
        habit = Habit("Exercise", "user_1", periodicity="daily")
        now = datetime.now()
        habit.complete(now - timedelta(days=1))
        habit.complete(now - timedelta(days=2))

        heatmap = HabitHeatmap(habit)
        assert len(heatmap.completion_dates) == 2

    def test_get_current_streak_with_completions(self):
        """Test get_current_streak with completions."""
        habit = Habit("Exercise", "user_1", periodicity="daily")
        now = datetime.now()
        for i in range(5):
            habit.complete(now - timedelta(days=i))

        heatmap = HabitHeatmap(habit)
        assert heatmap.get_current_streak() == 5

    def test_show_heatmap_with_completions(self):
        """Test that show() handles completions correctly."""
        habit = Habit("Exercise", "user_1", periodicity="daily")
        now = datetime.now()
        habit.complete(now - timedelta(days=1))
        habit.complete(now - timedelta(days=2))

        heatmap = HabitHeatmap(habit)
        result = heatmap.show()

        assert isinstance(result, str)
        assert "█" in result or "░" in result  # Should have filled/empty squares

    def test_heatmap_with_weekly_periodicity(self):
        """Test that HabitHeatmap works with weekly habits."""
        habit = Habit("Weekly Review", "user_1", periodicity="weekly")
        now = datetime.now()
        for i in range(3):
            habit.complete(now - timedelta(weeks=i))

        heatmap = HabitHeatmap(habit)
        assert heatmap.get_completion_count() == 3

    def test_heatmap_with_monthly_periodicity(self):
        """Test that HabitHeatmap works with monthly habits."""
        habit = Habit("Monthly Check", "user_1", periodicity="monthly")
        now = datetime.now()
        habit.complete(now - timedelta(days=30))
        habit.complete(now - timedelta(days=60))

        heatmap = HabitHeatmap(habit)
        assert heatmap.get_completion_count() == 2
