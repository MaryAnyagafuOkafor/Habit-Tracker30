"""
TESTS - Habit Model
====================

Unit tests for the Habit domain model.

Test Categories:
    - Habit Creation
    - Completion Management
    - Period Helper Methods
    - Serialization
    - Streak Methods
"""

from datetime import datetime, timedelta

from src.core.models.habit import Habit


class TestHabitCreation:
    """Tests for creating habits."""

    def test_create_basic_habit(self):
        """Test creating a basic habit with required fields."""
        habit = Habit("Exercise", "user_1", "Daily exercise", "daily")

        assert habit.name == "Exercise"
        assert habit.user_id == "user_1"
        assert habit.description == "Daily exercise"
        assert habit.periodicity == "daily"
        assert len(habit.completions) == 0
        assert habit.is_active is True


class TestHabitCompletions:
    """Tests for habit completion methods."""

    def test_complete_habit(self):
        """Test completing a habit adds a completion."""
        habit = Habit("Exercise", "user_1", periodicity="daily")
        assert len(habit.completions) == 0

        habit.complete()
        assert len(habit.completions) == 1
        assert isinstance(habit.completions[0], datetime)


class TestHabitEdit:
    """Tests for editing/updating habits."""

    def test_edit_habit_name(self):
        """Test changing a habit's name."""
        habit = Habit("Old Name", "user_1", "Description", "daily")
        assert habit.name == "Old Name"

        # Edit the name
        habit.name = "New Name"
        assert habit.name == "New Name"

        # Verify other fields unchanged
        assert habit.user_id == "user_1"
        assert habit.description == "Description"
        assert habit.periodicity == "daily"

    def test_edit_habit_description(self):
        """Test changing a habit's description."""
        habit = Habit("Exercise", "user_1", "Old description", "daily")
        assert habit.description == "Old description"

        # Edit the description
        habit.description = "New description"
        assert habit.description == "New description"

        # Verify other fields unchanged
        assert habit.name == "Exercise"
        assert habit.user_id == "user_1"
        assert habit.periodicity == "daily"

    def test_edit_habit_periodicity(self):
        """Test changing a habit's periodicity."""
        habit = Habit("Exercise", "user_1", "Description", "daily")
        assert habit.periodicity == "daily"

        # Edit the periodicity
        habit.periodicity = "weekly"
        assert habit.periodicity == "weekly"

        # Verify other fields unchanged
        assert habit.name == "Exercise"
        assert habit.user_id == "user_1"
        assert habit.description == "Description"

    def test_edit_habit_multiple_fields(self):
        """Test changing multiple fields at once."""
        habit = Habit(
            name="Old Name",
            user_id="user_1",
            description="Old description",
            periodicity="daily"
        )

        # Edit multiple fields
        habit.name = "New Name"
        habit.description = "New description"
        habit.periodicity = "weekly"

        assert habit.name == "New Name"
        assert habit.description == "New description"
        assert habit.periodicity == "weekly"
        assert habit.user_id == "user_1"  # Unchanged

    def test_edit_habit_preserves_completions(self):
        """Test that editing a habit preserves its completions."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Add completions
        today = datetime.now()
        for i in range(5):
            habit.complete(today - timedelta(days=i))

        completions_before = len(habit.completions)

        # Edit the habit
        habit.name = "New Exercise"
        habit.description = "New description"

        # Verify completions are preserved
        assert len(habit.completions) == completions_before
        # ✅ Check the most recent completion (index -1)
        assert habit.completions[-1].date() == today.date()

    def test_edit_habit_preserves_streak(self):
        """Test that editing a habit preserves its streak."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Build a streak
        today = datetime.now()
        for i in range(7):
            habit.complete(today - timedelta(days=i))

        streak_before = habit.get_current_streak()
        assert streak_before == 7

        # Edit the habit
        habit.name = "New Exercise"
        habit.description = "New description"

        # Verify streak is preserved
        streak_after = habit.get_current_streak()
        assert streak_after == 7

    def test_edit_habit_inactive(self):
        """Test editing an inactive habit."""
        habit = Habit("Exercise", "user_1", "Description", "daily")
        habit.is_active = False

        # Edit while inactive
        habit.name = "New Name"
        assert habit.name == "New Name"
        assert habit.is_active is False


class TestHabitDelete:
    """Tests for deleting/removing habits."""

    def test_habit_soft_delete(self):
        """Test soft deleting a habit."""
        habit = Habit("Exercise", "user_1", "Description", "daily")
        assert habit.is_active is True

        # Soft delete
        habit.is_active = False
        assert habit.is_active is False

        # Verify data is preserved
        assert habit.name == "Exercise"
        assert habit.user_id == "user_1"
        assert habit.description == "Description"
        assert habit.periodicity == "daily"

    def test_habit_soft_delete_preserves_completions(self):
        """Test that completions are preserved when soft deleting."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Add completions
        today = datetime.now()
        for i in range(3):
            habit.complete(today - timedelta(days=i))

        completions_before = len(habit.completions)

        # Soft delete
        habit.is_active = False

        # Verify completions are preserved
        assert len(habit.completions) == completions_before

    def test_habit_soft_delete_preserves_streak(self):
        """Test that streak is preserved when soft deleting."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Build a streak
        today = datetime.now()
        for i in range(5):
            habit.complete(today - timedelta(days=i))

        streak_before = habit.get_current_streak()
        assert streak_before == 5

        # Soft delete
        habit.is_active = False

        # Verify streak is preserved
        streak_after = habit.get_current_streak()
        assert streak_after == 5

    def test_habit_restore_after_delete(self):
        """Test restoring a soft-deleted habit."""
        habit = Habit("Exercise", "user_1", "Description", "daily")
        assert habit.is_active is True

        # Soft delete
        habit.is_active = False
        assert habit.is_active is False

        # Restore
        habit.is_active = True
        assert habit.is_active is True

        # Verify data is intact
        assert habit.name == "Exercise"
        assert habit.user_id == "user_1"
        assert habit.description == "Description"
        assert habit.periodicity == "daily"

    def test_habit_restore_preserves_completions(self):
        """Test that completions are preserved when restoring."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Add completions
        today = datetime.now()
        for i in range(3):
            habit.complete(today - timedelta(days=i))

        # Delete and restore
        habit.is_active = False
        habit.is_active = True

        # Verify completions are preserved
        assert len(habit.completions) == 3

    def test_habit_restore_preserves_streak(self):
        """Test that streak is preserved when restoring."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Build a streak
        today = datetime.now()
        for i in range(5):
            habit.complete(today - timedelta(days=i))

        streak_before = habit.get_current_streak()
        assert streak_before == 5

        # Delete and restore
        habit.is_active = False
        habit.is_active = True

        # Verify streak is preserved
        streak_after = habit.get_current_streak()
        assert streak_after == 5

    def test_habit_delete_clear_completions(self):
        """Test clearing all completions from a habit."""
        habit = Habit("Exercise", "user_1", "Description", "daily")

        # Add completions
        today = datetime.now()
        for i in range(3):
            habit.complete(today - timedelta(days=i))

        assert len(habit.completions) == 3

        # Clear completions
        habit.completions = []
        assert len(habit.completions) == 0

        # Verify habit data is intact
        assert habit.name == "Exercise"
        assert habit.user_id == "user_1"
        assert habit.description == "Description"
        assert habit.periodicity == "daily"


class TestHabitPeriodHelpers:
    """Tests for period helper methods."""

    def test_get_period_days_daily(self):
        habit = Habit("Exercise", "user_1", periodicity="daily")
        assert habit.get_period_days() == 1

    def test_get_period_days_weekly(self):
        habit = Habit("Exercise", "user_1", periodicity="weekly")
        assert habit.get_period_days() == 7

    def test_get_period_days_monthly(self):
        habit = Habit("Exercise", "user_1", periodicity="monthly")
        assert habit.get_period_days() == 30


class TestHabitSerialization:
    """Tests for habit serialization/deserialization."""

    def test_to_dict(self):
        habit = Habit("Exercise", "user_1", "Daily exercise", "daily")
        habit.complete(datetime(2024, 1, 15))
        data = habit.to_dict()
        assert data["name"] == "Exercise"
        assert data["periodicity"] == "daily"
        assert len(data["completions"]) == 1

    def test_from_dict(self):
        data = {
            "habit_id": "123",
            "user_id": "user_1",
            "name": "Exercise",
            "description": "Daily exercise",
            "periodicity": "daily",
            "created_at": "2024-01-15T10:00:00",
            "completions": ["2024-01-15T10:00:00"],
            "is_active": 1,
        }
        habit = Habit.from_dict(data)
        assert habit.habit_id == "123"
        assert habit.name == "Exercise"
        assert len(habit.completions) == 1


class TestHabitStreakMethods:
    """Tests for streak-related methods."""

    def test_get_current_streak_daily(self, test_habit_with_completions):
        streak = test_habit_with_completions.get_current_streak()
        assert streak == 5

    def test_get_longest_streak(self, test_habit_with_completions):
        longest = test_habit_with_completions.get_longest_streak()
        assert longest == 5

    def test_is_streak_complete(self):
        habit = Habit("Exercise", "user_1", periodicity="daily")
        today = datetime.now()
        for i in range(28):
            habit.complete(today - timedelta(days=i))
        assert habit.is_streak_complete() is True
