# tests/integration/test_habit_flow.py

"""
Integration tests for habit flow operations.
"""

from datetime import datetime, timedelta


class TestHabitFlow:
    """Integration tests for habit flow operations."""

    def test_full_edit_flow(self, manager, saved_test_user):
        """Test the complete edit flow from creation to editing."""
        # Create a habit
        habit = manager.create_habit(
            name="Original Habit",
            periodicity="daily",
            user_id=saved_test_user.user_id,  # ✅ Use saved_test_user
            description="Original description",
        )
        assert habit is not None  # ✅ Should pass now

        # Edit the habit
        result = manager.edit_habit(
            habit_id=habit.habit_id,
            name="Edited Habit",
            description="Edited description",
            periodicity="weekly",
        )
        assert result is True

        # Verify all changes
        updated = manager.get_habit_by_id(habit.habit_id)
        assert updated is not None
        assert updated.name == "Edited Habit"
        assert updated.description == "Edited description"
        assert updated.periodicity == "weekly"

        # Verify habit is still associated with the same user
        assert updated.user_id == saved_test_user.user_id

        # Verify completions are preserved
        assert len(updated.completions) == 0

    def test_edit_with_completions(self, manager, saved_test_user):
        """Test editing a habit that has completions."""
        # Create habit with completions
        habit = manager.create_habit(
            name="Exercise",
            periodicity="daily",
            user_id=saved_test_user.user_id,  # ✅ Use saved_test_user
            description="Daily exercise",
        )
        assert habit is not None  # ✅ Should pass now

        # Add completions
        today = datetime.now()
        for i in range(3):
            manager.storage.add_completion(habit.habit_id, today - timedelta(days=i))

        # Refresh habit to get completions
        habit = manager.get_habit_by_id(habit.habit_id)
        original_completions = len(habit.completions)
        assert original_completions == 3  # Verify completions were added

        # Edit the habit
        result = manager.rename_habit(habit.habit_id, "New Exercise Name")
        assert result is True

        # Verify completions are preserved
        updated = manager.get_habit_by_id(habit.habit_id)
        assert updated is not None
        assert updated.name == "New Exercise Name"
        assert len(updated.completions) == original_completions

    def test_edit_multiple_habits(self, manager, saved_test_user):
        """Test editing multiple habits."""
        # Create multiple habits
        habits = []
        for i in range(3):
            habit = manager.create_habit(
                name=f"Habit {i+1}",
                periodicity="daily",
                user_id=saved_test_user.user_id,  # ✅ Use saved_test_user
                description=f"Description {i+1}",
            )
            assert habit is not None
            habits.append(habit)

        # Edit each habit
        for i, habit in enumerate(habits):
            result = manager.rename_habit(habit.habit_id, f"Updated Habit {i+1}")
            assert result is True

        # Verify all were updated
        for i, habit in enumerate(habits):
            updated = manager.get_habit_by_id(habit.habit_id)
            assert updated is not None
            assert updated.name == f"Updated Habit {i+1}"

    def test_edit_habit_preserves_metadata(self, manager, saved_test_user):
        """Test that editing preserves creation date and ID."""
        # Create a habit
        habit = manager.create_habit(
            name="Original Habit",
            periodicity="daily",
            user_id=saved_test_user.user_id,  # ✅ Use saved_test_user
            description="Original description",
        )
        assert habit is not None

        original_id = habit.habit_id
        original_created_at = habit.created_at
        original_user_id = habit.user_id

        # Edit the habit
        result = manager.rename_habit(habit.habit_id, "New Name")
        assert result is True

        # Verify metadata preserved
        updated = manager.get_habit_by_id(original_id)
        assert updated is not None
        assert updated.habit_id == original_id
        assert updated.created_at == original_created_at
        assert updated.user_id == original_user_id

    def test_complete_habit_flow(self, manager, saved_test_user):
        """Test complete habit flow: create, complete, edit, delete."""
        # Create habit
        habit = manager.create_habit(
            name="Test Habit",
            periodicity="daily",
            user_id=saved_test_user.user_id,  # ✅ Use saved_test_user
            description="Test description",
        )
        assert habit is not None

        # Complete habit multiple times
        datetime.now()
        for i in range(5):
            result = manager.complete_habit(habit.habit_id)
            assert result is True

        # Refresh habit
        habit = manager.get_habit_by_id(habit.habit_id)
        assert len(habit.completions) == 5

        # Edit habit
        result = manager.edit_habit(
            habit_id=habit.habit_id,
            name="Edited Test Habit",
            description="Edited description",
        )
        assert result is True

        # Verify completions preserved
        updated = manager.get_habit_by_id(habit.habit_id)
        assert updated is not None
        assert updated.name == "Edited Test Habit"
        assert len(updated.completions) == 5

        # Delete habit
        result = manager.delete_habit(habit.habit_id)
        assert result is True

        # Verify habit is inactive
        deleted = manager.get_habit_by_id(habit.habit_id)
        assert deleted is None or deleted.is_active is False

    def test_habit_streak_preserved_after_edit(self, manager, saved_test_user):
        """Test that streak information is preserved after editing."""
        # Create habit with completions to build streak
        habit = manager.create_habit(
            name="Streak Habit",
            periodicity="daily",
            user_id=saved_test_user.user_id,  # ✅ Use saved_test_user
            description="Build a streak",
        )
        assert habit is not None

        # Add completions for 5 consecutive days
        today = datetime.now()
        for i in range(5):
            manager.storage.add_completion(habit.habit_id, today - timedelta(days=i))

        # Refresh habit
        habit = manager.get_habit_by_id(habit.habit_id)
        assert len(habit.completions) == 5

        # Get streak before edit
        from src.analytics.streak import StreakAnalyzer

        analyzer = StreakAnalyzer()
        streak_before = analyzer.get_streak_info(habit)
        assert streak_before["current"] == 5

        # Edit habit name only
        result = manager.rename_habit(habit.habit_id, "New Streak Habit")
        assert result is True

        # Get streak after edit
        updated = manager.get_habit_by_id(habit.habit_id)
        streak_after = analyzer.get_streak_info(updated)

        # Streak should be preserved
        assert streak_after["current"] == streak_before["current"]
        assert streak_after["longest"] == streak_before["longest"]
        assert updated.name == "New Streak Habit"
