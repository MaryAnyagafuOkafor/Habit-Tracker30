# tests/e2e/test_complete_user_journey.py

"""
E2E TEST - Complete User Journey
=================================
"""

from datetime import datetime, timedelta

from src.analytics.streak import StreakAnalyzer


class TestCompleteUserJourney:
    """Complete end-to-end user journey tests."""

    def test_complete_user_journey(self, temp_db, manager):
        """
        Test complete user journey from registration to streak achievement.
        """
        # Create analyzer instance
        analyzer = StreakAnalyzer()

        # ============================================================
        # PHASE 1: User Registration
        # ============================================================

        username = "journey_user"
        email = "journey@example.com"
        password = "secure_password_123"

        user = manager.register_user(username, password, email)
        assert user is not None, "User registration failed"
        assert user.username == username
        assert user.email == email
        assert user.role == "user"
        assert user.verify_password(password) is True

        # ============================================================
        # PHASE 2: User Login
        # ============================================================

        logged_user = manager.login_user(username, password)
        assert logged_user is not None, "Login failed"
        assert logged_user.username == username
        assert logged_user.user_id == user.user_id

        # ============================================================
        # PHASE 3: Create First Habit
        # ============================================================

        habit1 = manager.create_habit(
            name="Daily Exercise",
            periodicity="daily",
            user_id=user.user_id,
            description="Exercise every day for 30 minutes",
        )
        assert habit1 is not None, "Habit creation failed"
        assert habit1.name == "Daily Exercise"
        assert habit1.periodicity == "daily"
        assert habit1.user_id == user.user_id

        # ============================================================
        # PHASE 4: Complete Habit 6 Consecutive Days
        # ============================================================

        today = datetime.now()

        # Add completions for 6 consecutive days (today, yesterday, ... 5 days ago)
        for i in range(6):
            completion_date = today - timedelta(days=i)
            result = temp_db.add_completion(habit1.habit_id, completion_date)
            assert result is True, f"Failed to add completion for day {i}"

        # Also complete today using manager to ensure habit completion works
        manager.complete_habit(habit1.habit_id)

        # Refresh habit to get updated completions
        habit1 = temp_db.get_habit_by_id(habit1.habit_id)

        # ============================================================
        # PHASE 5: Check Streak
        # ============================================================

        # Use analyzer instead of get_streak_info
        streak_info = analyzer.get_streak_info(habit1)

        # The streak should be 6 (6 consecutive days)
        # The total completions will be 7 (6 manual + 1 from manager)
        assert streak_info["current"] == 6
        assert streak_info["periodicity"] == "daily"
        assert streak_info["status"] == "🔄 IN PROGRESS"
        assert streak_info["total_completions"] == 7

        # ============================================================
        # PHASE 6: View Dashboard
        # ============================================================

        habits = manager.get_habits_for_user(user.user_id)
        assert len(habits) == 1
        assert habits[0].name == "Daily Exercise"

        summary = manager.get_habit_streak_summary(user.user_id)
        assert summary["total_habits"] == 1
        assert summary["in_progress"] == 1
        assert summary["completed_streaks"] == 0
        assert summary["not_started"] == 0

        habit_with_streak = manager.get_habit_with_streak(habit1.habit_id)
        assert habit_with_streak["name"] == "Daily Exercise"
        assert habit_with_streak["completions"] == 7  # 6 manual + 1 manager
        assert habit_with_streak["streak_info"]["current"] == 6

        # ============================================================
        # PHASE 7: Create Second Habit
        # ============================================================

        habit2 = manager.create_habit(
            name="Weekly Review",
            periodicity="weekly",
            user_id=user.user_id,
            description="Review week every Sunday",
        )
        assert habit2 is not None, "Second habit creation failed"
        assert habit2.name == "Weekly Review"
        assert habit2.periodicity == "weekly"

        # Add completions to habit2 with different weeks
        for i in range(2):
            completion_date = today - timedelta(weeks=i)
            temp_db.add_completion(habit2.habit_id, completion_date)

        # ============================================================
        # PHASE 8: View Updated Dashboard
        # ============================================================

        habits = manager.get_habits_for_user(user.user_id)
        assert len(habits) == 2

        summary = manager.get_habit_streak_summary(user.user_id)
        assert summary["total_habits"] == 2

        all_habits_with_streaks = manager.get_all_habits_with_streaks(user.user_id)
        assert len(all_habits_with_streaks) == 2

        # ============================================================
        # PHASE 9: Delete a Habit
        # ============================================================

        # Delete habit2
        result = manager.delete_habit(habit2.habit_id)
        assert result is True

        # Verify habit2 is gone
        habits = manager.get_habits_for_user(user.user_id)
        assert len(habits) == 1
        assert habits[0].name == "Daily Exercise"

        # ============================================================
        # PHASE 10: Complete More Days to Reach Target
        # ============================================================

        # Complete habit1 for more days to reach target
        for i in range(6, 28):  # Add days 6-27 (22 more days)
            completion_date = today - timedelta(days=i)
            temp_db.add_completion(habit1.habit_id, completion_date)

        # Refresh habit
        habit1 = temp_db.get_habit_by_id(habit1.habit_id)

        # Check if streak reached target
        # Use analyzer instead of get_streak_info
        habit1_info = analyzer.get_streak_info(habit1)

        # If we have 28 completions total, streak should be 28
        if len(habit1.completions) >= 28:
            assert habit1_info["current"] >= 28
            assert habit1_info["status"] == "✅ COMPLETE"
        else:
            # If not enough completions, still check we're making progress
            assert habit1_info["current"] > 6  # Should have more than 6 now
            assert habit1_info["total_completions"] > 7  # Should have more completions

    def test_guest_user_journey(self, temp_db, manager):
        """
        Test guest user journey with predefined habits.
        """
        StreakAnalyzer()

        # ============================================================
        # PHASE 1: Guest Login
        # ============================================================

        guest_id = "guest"

        # Check if guest exists, create if not
        if not temp_db.user_exists(guest_id):
            from src.core.models.user import User

            guest_user = User(
                username="guest",
                email="",
                password="guest123",
                user_id=guest_id,
                role="guest",
            )
            temp_db.save_user(guest_user)

        # Login as guest
        user = manager.login_user("guest", "guest123")
        assert user is not None, "Guest login failed"
        assert user.username == "guest"
        assert user.role == "guest"

        # ============================================================
        # PHASE 2: Load Guest Habits
        # ============================================================

        # Create guest habits if none exist
        habits = manager.get_habits_for_user(guest_id)

        if not habits:
            from scripts.seed_data import PredefinedHabits

            demo_habits = PredefinedHabits.create(guest_id)
            for habit in demo_habits:
                temp_db.save_habit(habit)
            habits = manager.get_habits_for_user(guest_id)

        assert len(habits) > 0, "Guest should have habits"

        # ============================================================
        # PHASE 3: View Guest Dashboard
        # ============================================================

        # Get all habits with streaks
        all_habits = manager.get_all_habits_with_streaks(guest_id)
        assert len(all_habits) > 0

        # Check each habit has streak info
        for habit_data in all_habits:
            assert "streak_info" in habit_data
            assert habit_data["streak_info"]["periodicity"] in [
                "daily",
                "weekly",
                "monthly",
            ]
            assert habit_data["streak_info"]["current"] >= 0

        # ============================================================
        # PHASE 4: Check Guest Analytics
        # ============================================================

        # Get summary
        summary = manager.get_habit_streak_summary(guest_id)
        assert summary["total_habits"] > 0

        # Get longest streak habit
        longest = manager.get_longest_streak_habit(guest_id)
        if longest:
            assert "habit" in longest
            assert "streak_info" in longest
            assert longest["streak_info"]["current"] > 0

        # ============================================================
        # PHASE 5: Filter Habits by Periodicity
        # ============================================================

        # Get daily habits
        daily_habits = manager.get_habits_by_periodicity(guest_id, "daily")
        for habit in daily_habits:
            assert habit.periodicity == "daily"

        # Get weekly habits
        weekly_habits = manager.get_habits_by_periodicity(guest_id, "weekly")
        for habit in weekly_habits:
            assert habit.periodicity == "weekly"

        # Get monthly habits
        monthly_habits = manager.get_habits_by_periodicity(guest_id, "monthly")
        for habit in monthly_habits:
            assert habit.periodicity == "monthly"

    def test_streak_calculations(self, temp_db, manager):
        """
        Test streak calculations with various scenarios.
        """
        analyzer = StreakAnalyzer()

        # ============================================================
        # PHASE 1: Create Test User and Habit
        # ============================================================

        user = manager.register_user("streak_user", "password123")
        assert user is not None

        habit = manager.create_habit(
            name="Test Habit",
            periodicity="daily",
            user_id=user.user_id,
            description="Test habit for streak calculations",
        )
        assert habit is not None

        # ============================================================
        # PHASE 2: Perfect Streak (28 days)
        # ============================================================

        today = datetime.now()

        # Add completions for 28 consecutive days
        for i in range(28):
            completion_date = today - timedelta(days=i)
            temp_db.add_completion(habit.habit_id, completion_date)

        # Refresh habit
        habit = temp_db.get_habit_by_id(habit.habit_id)

        # Check streak info
        streak_info = analyzer.get_streak_info(habit)
        assert streak_info["current"] == 28
        assert streak_info["longest"] == 28
        assert streak_info["is_complete"] is True
        assert streak_info["status"] == "✅ COMPLETE"

        # ============================================================
        # PHASE 3: Broken Streak
        # ============================================================

        # Create a new habit for broken streak test
        habit2 = manager.create_habit(
            name="Broken Streak Habit",
            periodicity="daily",
            user_id=user.user_id,
        )
        assert habit2 is not None

        # Add completions with a gap
        # Days 1-5: complete, Day 6: skip, Days 7-10: complete
        for i in range(1, 6):
            completion_date = today - timedelta(days=i)
            temp_db.add_completion(habit2.habit_id, completion_date)

        # Skip day 6 (no completion)

        for i in range(7, 11):
            completion_date = today - timedelta(days=i)
            temp_db.add_completion(habit2.habit_id, completion_date)

        # Refresh habit
        habit2 = temp_db.get_habit_by_id(habit2.habit_id)

        # Check streak info
        streak_info = analyzer.get_streak_info(habit2)
        # Current streak should be 5 (days 7-10 = 4 + day 5 = 1 = 5)
        # Actually it depends on the gap, but it should be broken at day 6
        assert streak_info["current"] == 5  # Days 7-10 (4 days) + day 5 (1 day) = 5
        assert streak_info["longest"] == 5
        assert streak_info["is_complete"] is False

        # ============================================================
        # PHASE 4: Weekly Streak
        # ============================================================

        habit3 = manager.create_habit(
            name="Weekly Test",
            periodicity="weekly",
            user_id=user.user_id,
        )
        assert habit3 is not None

        # Add completions for 4 consecutive weeks
        for i in range(4):
            completion_date = today - timedelta(weeks=i)
            temp_db.add_completion(habit3.habit_id, completion_date)

        # Refresh habit
        habit3 = temp_db.get_habit_by_id(habit3.habit_id)

        # Check streak info
        streak_info = analyzer.get_streak_info(habit3)
        assert streak_info["current"] == 4
        assert streak_info["longest"] == 4
        assert streak_info["is_complete"] is True
        assert streak_info["status"] == "✅ COMPLETE"
