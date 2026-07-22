# tests/e2e/test_multi_user_scenario.py

"""
E2E TEST - Multi-User Scenarios
================================

End-to-end tests for scenarios involving multiple users.

Scenarios:
    1. User data isolation
    2. Duplicate usernames blocked
    3. Guest and regular users coexist
    4. Multiple users have independent streaks
"""

from datetime import datetime, timedelta

from src.core.models.user import User
from src.core.services.habit_service import HabitManager


class TestMultiUserScenarios:
    """End-to-end tests for multi-user scenarios."""

    def test_user_data_isolation(self, temp_db):
        """E2E: Users cannot see each other's data."""
        storage = temp_db
        manager = HabitManager(storage)

        user1 = manager.register_user("user_a", "a@email.com", "pass_a")
        user2 = manager.register_user("user_b", "b@email.com", "pass_b")
        assert user1 is not None
        assert user2 is not None

        # ✅ Fix: Correct argument order: name, periodicity, user_id, description
        habit_a = manager.create_habit(
            name="A's habit",
            periodicity="daily",
            user_id=user1.user_id,
            description="Habit for user A",
        )
        assert habit_a is not None

        habit_b = manager.create_habit(
            name="B's habit",
            periodicity="daily",
            user_id=user2.user_id,
            description="Habit for user B",
        )
        assert habit_b is not None

        user_a_habits = manager.get_habits_for_user(user1.user_id)
        assert len(user_a_habits) == 1
        assert user_a_habits[0].name == "A's habit"

        user_b_habits = manager.get_habits_for_user(user2.user_id)
        assert len(user_b_habits) == 1
        assert user_b_habits[0].name == "B's habit"

    def test_duplicate_usernames_blocked(self, temp_db):
        """E2E: Duplicate usernames are not allowed."""
        storage = temp_db
        manager = HabitManager(storage)

        user1 = manager.register_user("same_name", "first@email.com", "pass")
        assert user1 is not None

        user2 = manager.register_user("same_name", "second@email.com", "pass")
        assert user2 is None, "Duplicate username should be blocked"

        user3 = manager.register_user("different_name", "third@email.com", "pass")
        assert user3 is not None

    def test_guest_and_regular_user_coexist(self, temp_db):
        """E2E: Guest and regular users coexist."""
        storage = temp_db
        manager = HabitManager(storage)

        guest = User(
            username="guest",
            email="",
            password="guest123",
            user_id="guest",
            role="guest",
        )
        storage.save_user(guest)

        regular = manager.register_user("regular_user", "regular@email.com", "pass")
        assert regular is not None

        all_users = storage.get_all_users()
        assert len(all_users) == 2

        guest_retrieved = storage.get_user_by_id("guest")
        assert guest_retrieved.role == "guest"

    def test_multiple_users_independent_streaks(self, temp_db):
        """E2E: Multiple users have independent streaks."""
        storage = temp_db
        manager = HabitManager(storage)

        user1 = manager.register_user("streak_user1", "s1@email.com", "pass1")
        user2 = manager.register_user("streak_user2", "s2@email.com", "pass2")
        assert user1 is not None
        assert user2 is not None

        # ✅ Fix: Correct argument order
        habit1 = manager.create_habit(
            name="User1 Daily",
            periodicity="daily",
            user_id=user1.user_id,
            description="User1 daily habit",
        )
        assert habit1 is not None

        habit2 = manager.create_habit(
            name="User2 Daily",
            periodicity="daily",
            user_id=user2.user_id,
            description="User2 daily habit",
        )
        assert habit2 is not None

        today = datetime.now()
        for i in range(5):
            habit1.complete(today - timedelta(days=i))
        storage.save_habit(habit1)

        for i in range(2):
            habit2.complete(today - timedelta(days=i))
        storage.save_habit(habit2)

        streak1 = storage.get_streak_for_habit(habit1.habit_id)
        assert streak1["current"] == 5

        streak2 = storage.get_streak_for_habit(habit2.habit_id)
        assert streak2["current"] == 2
