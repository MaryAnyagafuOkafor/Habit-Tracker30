"""
E2E TEST - Guest Journey
==========================

Full end-to-end test of a guest user's journey.

Journey Phases:
    1. Guest login
    2. View pre-populated habits
    3. Explore features
    4. Register as a real user
    5. Guest habits preserved
"""

from src.core.models.user import User
from src.core.services.habit_service import HabitManager
from src.analytics.heatmap import HabitHeatmap
from scripts.seed_data import PredefinedHabits


class TestGuestJourney:
    """Full end-to-end test of a guest user's journey."""

    def test_guest_journey_to_registration(self, temp_db):
        """E2E: Guest login to registration flow."""
        storage = temp_db
        manager = HabitManager(storage)

        # ============================================================
        # PHASE 1: GUEST LOGIN
        # ============================================================

        guest_id = "guest"
        guest_user = User(
            username="guest",
            email="",
            password="guest123",
            user_id=guest_id,
            role="guest",
        )
        storage.save_user(guest_user)

        guest = manager.login_user("guest", "guest123")
        assert guest is not None
        assert guest.role == "guest"

        # ============================================================
        # PHASE 2: CREATE GUEST HABITS
        # ============================================================

        demo_habits = PredefinedHabits.create(guest_id)
        for habit in demo_habits:
            manager.save_habit_direct(habit)

        guest_habits = manager.get_habits_for_user(guest_id)
        assert len(guest_habits) > 0
        assert len(guest_habits) == 7  # 3 daily + 2 weekly + 2 monthly

        # ============================================================
        # PHASE 3: GUEST EXPLORES FEATURES
        # ============================================================

        first_habit = guest_habits[0]
        streak_info = storage.get_streak_for_habit(first_habit.habit_id)
        assert streak_info is not None

        all_guest_habits = storage.get_all_habits_with_streaks(guest_id)
        assert len(all_guest_habits) == len(guest_habits)

        heatmap = HabitHeatmap(first_habit)
        completion_count = heatmap.get_completion_count()
        assert completion_count >= 0

        # ============================================================
        # PHASE 4: GUEST REGISTERS
        # ============================================================

        new_username = "guest_turned_user"
        new_email = "guest@example.com"
        new_password = "new_password_123"

        registered_user = manager.register_user(new_username, new_email, new_password)
        assert registered_user is not None
        assert registered_user.role == "user"

        user_habits = manager.get_habits_for_user(registered_user.user_id)
        assert len(user_habits) == 0

        # ============================================================
        # PHASE 5: GUEST HABITS PRESERVED
        # ============================================================

        still_guest_habits = manager.get_habits_for_user(guest_id)
        assert len(still_guest_habits) == len(guest_habits)
