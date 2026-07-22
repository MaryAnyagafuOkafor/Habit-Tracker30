# tests/unit/services/test_habit_service.py

"""
TESTS - Habit Service Layer
========================================

Simple, organized tests for HabitManager service layer.
All tests follow the same pattern: Create → Act → Assert
"""

from datetime import datetime, timedelta


# ============================================================
# TEST: CREATE HABIT
# ============================================================

class TestCreateHabit:
    """Tests for creating habits."""

    def test_create_habit(self, manager, test_user):
        """Test creating a habit."""
        habit = manager.create_habit(
            name="Exercise",
            periodicity="daily",
            user_id=test_user.user_id,
            description="Daily exercise"
        )
        assert habit is not None
        assert habit.name == "Exercise"

    def test_create_habit_no_description(self, manager, test_user):
        """Test creating a habit without description."""
        habit = manager.create_habit(
            name="Exercise",
            periodicity="daily",
            user_id=test_user.user_id
        )
        assert habit is not None

    def test_create_habit_invalid_periodicity(self, manager, test_user):
        """Test creating habit with invalid periodicity."""
        habit = manager.create_habit(
            name="Invalid",
            periodicity="invalid",
            user_id=test_user.user_id
        )
        assert habit is None


# ============================================================
# TEST: VIEW HABITS
# ============================================================

class TestViewHabits:
    """Tests for viewing habits."""

    def test_get_habits_for_user(self, manager, test_user):
        """Test getting all habits for a user."""
        manager.create_habit("Habit 1", "daily", test_user.user_id)
        manager.create_habit("Habit 2", "weekly", test_user.user_id)

        habits = manager.get_habits_for_user(test_user.user_id)
        assert len(habits) == 2

    def test_get_habit_by_id(self, manager, test_user):
        """Test getting a habit by ID."""
        created = manager.create_habit("Exercise", "daily", test_user.user_id)
        habit = manager.get_habit_by_id(created.habit_id)
        assert habit is not None
        assert habit.name == "Exercise"


# ============================================================
# TEST: UPDATE HABIT
# ============================================================

class TestUpdateHabit:
    """Tests for updating habits."""

    def test_update_habit_name(self, manager, test_user):
        """Test updating a habit's name."""
        # Create
        habit = manager.create_habit("Old Name", "daily", test_user.user_id)

        # Update
        habit.name = "New Name"
        manager.save_habit_direct(habit)

        # Verify
        updated = manager.get_habit_by_id(habit.habit_id)
        assert updated.name == "New Name"

    def test_update_habit_description(self, manager, test_user):
        """Test updating a habit's description."""
        # Create
        habit = manager.create_habit(
            "Exercise",
            "daily",
            test_user.user_id,
            "Old description"
        )

        # Update
        habit.description = "New description"
        manager.save_habit_direct(habit)

        # Verify
        updated = manager.get_habit_by_id(habit.habit_id)
        assert updated.description == "New description"


# ============================================================
# TEST: DELETE HABIT
# ============================================================

class TestDeleteHabit:
    """Tests for deleting habits."""

    def test_delete_habit(self, manager, test_user):
        """Test deleting a habit."""
        # Create
        habit = manager.create_habit("To Delete", "daily", test_user.user_id)

        # Delete
        result = manager.delete_habit(habit.habit_id)
        assert result is True

        # Verify
        deleted = manager.get_habit_by_id(habit.habit_id)
        assert deleted is None or not deleted.is_active

    def test_delete_habit_not_found(self, manager):
        """Test deleting non-existent habit."""
        result = manager.delete_habit("nonexistent")
        assert result is False



# ============================================================
# TEST: COMPLETE HABIT
# ============================================================

class TestCompleteHabit:
    """Tests for completing habits."""

    def test_complete_habit(self, manager, test_user):
        """Test completing a habit."""
        # Create
        habit = manager.create_habit("Exercise", "daily", test_user.user_id)

        # Complete
        result = manager.complete_habit(habit.habit_id)
        assert result is True

        # Verify
        completions = manager.storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 1

    def test_complete_habit_multiple_times(self, manager, test_user):
        """Test completing a habit multiple times."""
        # Create
        habit = manager.create_habit("Exercise", "daily", test_user.user_id)

        # Complete 3 times
        for i in range(3):
            manager.complete_habit(habit.habit_id)

        # Verify
        completions = manager.storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 3

    def test_complete_habit_not_found(self, manager):
        """Test completing non-existent habit."""
        result = manager.complete_habit("nonexistent")
        assert result is False


# ============================================================
# TEST: USER MANAGEMENT
# ============================================================

class TestUserManagement:
    """Tests for user management."""

    def test_register_user(self, manager):
        """Test registering a user."""
        user = manager.register_user("newuser", "password", "new@email.com")
        assert user is not None
        assert user.username == "newuser"

    def test_register_user_duplicate(self, manager, test_user):
        """Test registering duplicate user."""
        user2 = manager.register_user("testuser", "password", "test@email.com")
        assert user2 is None

    def test_login_user(self, manager, test_user):
        """Test logging in."""
        user = manager.login_user("testuser", "password")
        assert user is not None
        assert user.username == "testuser"

    def test_login_user_wrong_password(self, manager, test_user):
        """Test login with wrong password."""
        user = manager.login_user("testuser", "wrong")
        assert user is None


# ============================================================
# TEST: STREAK AND ANALYTICS
# ============================================================

class TestStreakAnalytics:
    """Tests for streak analytics."""

    def test_get_habit_with_streak(self, manager, test_user):
        """Test getting habit with streak."""
        # Create
        habit = manager.create_habit("Exercise", "daily", test_user.user_id)

        # Add completions
        now = datetime.now()
        for i in range(5):
            manager.storage.add_completion(habit.habit_id, now - timedelta(days=i))

        # Get streak
        result = manager.get_habit_with_streak(habit.habit_id)
        assert result["completions"] == 5
        assert result["streak_info"]["current"] == 5

    def test_get_habit_streak_summary(self, manager, test_user):
        """Test getting streak summary."""
        # Create habits
        habit1 = manager.create_habit("Daily Exercise", "daily", test_user.user_id)
        habit2 = manager.create_habit("Weekly Review", "weekly", test_user.user_id)

        # Add completions
        now = datetime.now()
        for i in range(5):
            manager.storage.add_completion(habit1.habit_id, now - timedelta(days=i))

        for i in range(4):
            manager.storage.add_completion(habit2.habit_id, now - timedelta(weeks=i))

        # Get summary
        summary = manager.get_habit_streak_summary(test_user.user_id)
        assert summary["total_habits"] == 2