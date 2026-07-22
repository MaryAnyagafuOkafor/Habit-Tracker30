# tests/unit/models/test_seed_data.py

"""
TESTS - Seed Data
==================

Unit tests for the seed data generation.
"""

import sys
from pathlib import Path

# ✅ Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.models.user import User  # noqa: E402
from src.core.models.habit import Habit  # noqa: E402
from core.services.habit_service import HabitManager  # noqa: E402

# ✅ Import from scripts folder using the full path
from scripts.seed_data import (  # noqa: E402
    create_users,
    create_habits_for_user,
    add_4_weeks_completions,
    DAILY_HABITS,
    WEEKLY_HABITS,
    MONTHLY_HABITS,
    ALL_HABITS,
    PredefinedHabits,
)


class TestSeedDataUsers:
    """Tests for user creation in seed data."""

    def test_create_users_creates_guest_only(self, temp_db):
        """Test that create_users creates only guest user."""
        storage = temp_db
        users = create_users(storage)

        assert len(users) == 1
        assert users[0].username == "guest"
        assert users[0].role == "guest"


class TestPredefinedHabitsTemplates:
    """Tests for predefined habit templates."""

    def test_all_habits_has_seven_habits(self):
        """Test that ALL_HABITS contains exactly 7 habits."""
        assert len(ALL_HABITS) == 7

    def test_daily_habits_has_three_habits(self):
        """Test that DAILY_HABITS contains exactly 3 habits."""
        assert len(DAILY_HABITS) == 3

    def test_weekly_habits_has_two_habits(self):
        """Test that WEEKLY_HABITS contains exactly 2 habits."""
        assert len(WEEKLY_HABITS) == 2

    def test_monthly_habits_has_two_habits(self):
        """Test that MONTHLY_HABITS contains exactly 2 habits."""
        assert len(MONTHLY_HABITS) == 2

    def test_all_habits_has_patterns(self):
        """Test that all habits have pattern defined."""
        for habit in ALL_HABITS:
            assert "pattern" in habit
            assert habit["pattern"] in ["perfect", "struggling", "in_progress"]


class TestCreateHabitsForUser:
    """Tests for creating habits for a user."""

    def test_create_habits_creates_seven_habits(self, temp_db, test_user):
        """Test that create_habits_for_user creates 7 habits."""
        storage = temp_db
        storage.save_user(test_user)

        habits = create_habits_for_user(storage, test_user)
        assert len(habits) == 7

    def test_create_habits_has_correct_periodicities(self, temp_db, test_user):
        """Test that habits have correct periodicities."""
        storage = temp_db
        storage.save_user(test_user)

        habits = create_habits_for_user(storage, test_user)

        daily = [h for h in habits if h.periodicity == "daily"]
        weekly = [h for h in habits if h.periodicity == "weekly"]
        monthly = [h for h in habits if h.periodicity == "monthly"]

        assert len(daily) == 3
        assert len(weekly) == 2
        assert len(monthly) == 2

    def test_create_habits_saves_to_database(self, temp_db, test_user):
        """Test that habits are saved to the database."""
        storage = temp_db
        storage.save_user(test_user)

        create_habits_for_user(storage, test_user)

        saved_habits = storage.get_habits_for_user(test_user.user_id)
        assert len(saved_habits) == 7


class TestFourWeeksCompletions:
    """Tests for 4 weeks completion patterns."""

    def test_perfect_pattern_has_28_completions(self, temp_db, test_user):
        """Test that perfect pattern creates 28 completions."""
        storage = temp_db
        storage.save_user(test_user)

        habit = Habit(
            name="Morning Exercise",
            user_id=test_user.user_id,
            description="30 minutes of physical activity",
            periodicity="daily",
        )
        storage.save_habit(habit)

        count = add_4_weeks_completions(storage, habit, "perfect")
        assert count == 28

        completions = storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 28

    def test_struggling_pattern_has_11_completions(self, temp_db, test_user):
        """Test that struggling pattern creates 11 completions."""
        storage = temp_db
        storage.save_user(test_user)

        habit = Habit(
            name="Read Daily",
            user_id=test_user.user_id,
            description="Read 20 pages",
            periodicity="daily",
        )
        storage.save_habit(habit)

        count = add_4_weeks_completions(storage, habit, "struggling")
        assert count == 11

        completions = storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 11

    def test_in_progress_pattern_has_20_completions(self, temp_db, test_user):
        """Test that in_progress pattern creates 20 completions."""
        storage = temp_db
        storage.save_user(test_user)

        habit = Habit(
            name="Meditate",
            user_id=test_user.user_id,
            description="10 minutes meditation",
            periodicity="daily",
        )
        storage.save_habit(habit)

        count = add_4_weeks_completions(storage, habit, "in_progress")
        assert count == 20

        completions = storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 20


class TestGuestAccountSeed:
    """Tests for the complete guest account seed data."""

    def test_guest_has_seven_habits(self, temp_db):
        """Test that guest account has exactly 7 habits."""
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

        demo_habits = PredefinedHabits.create("guest")
        for habit in demo_habits:
            manager.save_habit_direct(habit)

        habits = manager.get_habits_for_user("guest")
        assert len(habits) == 7

    def test_guest_has_correct_periodicities(self, temp_db):
        """Test that guest has correct mix of habit periodicities."""
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

        demo_habits = PredefinedHabits.create("guest")
        for habit in demo_habits:
            manager.save_habit_direct(habit)

        habits = manager.get_habits_for_user("guest")

        daily = [h for h in habits if h.periodicity == "daily"]
        weekly = [h for h in habits if h.periodicity == "weekly"]
        monthly = [h for h in habits if h.periodicity == "monthly"]

        assert len(daily) == 3
        assert len(weekly) == 2
        assert len(monthly) == 2

    def test_guest_habits_have_completions(self, temp_db):
        """Test that guest habits have completion data."""
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

        demo_habits = PredefinedHabits.create("guest")
        for habit in demo_habits:
            manager.save_habit_direct(habit)

        habits = manager.get_habits_for_user("guest")

        for habit in habits:
            completions = storage.get_habit_completions(habit.habit_id)
            assert len(completions) > 0
