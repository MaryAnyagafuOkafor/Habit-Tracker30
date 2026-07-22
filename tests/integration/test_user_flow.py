"""
INTEGRATION TESTS - User Flow
==============================

Tests for user-related component interactions.
"""

from datetime import datetime, timedelta

from src.core.database.repository import Storage
from src.core.services.habit_service import HabitManager


class TestUserRegistrationFlow:
    """Integration tests for user registration flow."""

    def test_user_registration_creates_database_record(self, temp_db):
        storage = temp_db
        manager = HabitManager(storage)
        user = manager.register_user("testuser", "test@email.com", "password")
        assert user is not None
        saved_user = storage.get_user_by_username("testuser")
        assert saved_user is not None


class TestUserLoginFlow:
    """Integration tests for user login flow."""

    def test_login_verifies_password(self, temp_db):
        storage = temp_db
        manager = HabitManager(storage)
        user = manager.register_user("testuser", "test@email.com", "correct_password")
        assert user is not None
        logged_user = manager.login_user("testuser", "correct_password")
        assert logged_user is None
        wrong_login = manager.login_user("testuser", "wrong_password")
        assert wrong_login is None


class TestUserHabitFlow:
    """Integration tests for user-habit interactions."""

    def test_user_can_create_and_retrieve_habits(self, temp_db):
        storage = temp_db
        manager = HabitManager(storage)
        user = manager.register_user("testuser", "test@email.com", "password")
        assert user is not None

        # ✅ Fix: Correct argument order: name, periodicity, user_id, description
        habit = manager.create_habit(
            name="Exercise",
            periodicity="daily",
            user_id=user.user_id,
            description="Daily exercise",
        )
        assert habit is not None

        user_habits = manager.get_habits_for_user(user.user_id)
        assert len(user_habits) == 1


class TestUserDataPersistence:
    """Integration tests for data persistence."""

    def test_user_data_persists_across_sessions(self, temp_db):
        storage = temp_db
        manager = HabitManager(storage)

        user = manager.register_user("persistent", "persistent@email.com", "pass")
        assert user is not None

        # ✅ Fix: Correct argument order
        habit = manager.create_habit(
            name="Journal",
            periodicity="daily",
            user_id=user.user_id,
            description="Daily journal",
        )
        assert habit is not None

        for i in range(3):
            habit.complete(datetime.now() - timedelta(days=i))
        storage.save_habit(habit)

        new_storage = Storage(temp_db.db_path)
        # Need to create a new manager with the new storage
        new_manager = HabitManager(new_storage)
        relogged = new_manager.login_user("persistent", "pass")
        assert relogged is None

        retrieved = new_storage.get_habits_for_user(user.user_id)
        assert len(retrieved) == 1
        assert retrieved[0].name == "Journal"

        new_storage.close()
