# src/core/services/habit_service.py

from typing import Optional, List, Dict, Any
from src.core.database.repository import Storage
from src.core.models.habit import Habit
from src.core.models.user import User
from src.analytics.streak import StreakAnalyzer


class HabitManager:
    """Service layer for habit management."""

    def __init__(self, storage: Storage):
        """
        Initialize the habit manager.

        Args:
            storage: Database storage instance
        """
        self.storage = storage
        self.analyzer = StreakAnalyzer()  # Create analyzer instance

    # ============================================
    # USER MANAGEMENT
    # ============================================

    def register_user(
        self, username: str, password: str, email: str = "", role: str = "user"
    ) -> Optional[User]:
        """
        Register a new user.

        Args:
            username: Username for the new user
            password: Password for the new user
            email: Email address (optional)
            role: User role (default: "user")

        Returns:
            User object if registration successful, None otherwise
        """
        # Validate inputs
        if not username or not password:
            print("❌ Username and password are required")
            return None

        # Check if username already exists
        if self.storage.username_exists(username):
            print(f"❌ Username '{username}' already exists")
            return None

        # Create user
        user = User(username=username, password=password, email=email, role=role)

        # Save to database
        try:
            self.storage.save_user(user)
            return user
        except Exception as e:
            print(f"❌ Error registering user: {e}")
            return None

    def login_user(self, username: str, password: str) -> Optional[User]:
        """
        Login a user.

        Args:
            username: Username
            password: Password

        Returns:
            User object if login successful, None otherwise
        """
        if not username or not password:
            print("❌ Username and password required")
            return None

        user = self.storage.get_user_by_username(username)

        if not user:
            print(f"❌ User '{username}' not found")
            return None

        if not user.is_active:
            print("❌ Account is deactivated")
            return None

        if user.verify_password(password):
            return user
        else:
            print("❌ Invalid password")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        return self.storage.get_user_by_id(user_id)

    def get_username_by_id(self, user_id: str) -> Optional[str]:
        """Get username by user ID."""
        user = self.storage.get_user_by_id(user_id)
        return user.username if user else None

    def get_all_users(self) -> List[User]:
        """Get all users (admin function)."""
        return self.storage.get_all_users()

    # ============================================
    # HABIT MANAGEMENT
    # ============================================

    def create_habit(
        self,
        name: str,
        periodicity: str,
        user_id: str,
        description: Optional[str] = None,
    ) -> Optional[Habit]:
        """
        Create a new habit for a user.

        Args:
            name: Name of the habit
            periodicity: "daily", "weekly", or "monthly"
            user_id: ID of the user creating the habit
            description: Optional description of the habit

        Returns:
            Habit object if created successfully, None otherwise
        """
        # Validate periodicity
        if periodicity not in ["daily", "weekly", "monthly"]:
            return None

        if not self.storage.user_exists(user_id):
            print(f"❌ User {user_id} not found")
            return None

        # Create the habit
        habit = Habit(
            name=name, user_id=user_id, description=description, periodicity=periodicity
        )

        # Save to database
        if self.storage.save_habit(habit):
            return habit
        return None

    def get_habit_by_id(self, habit_id: str) -> Optional[Habit]:
        """Get a habit by its ID."""
        return self.storage.get_habit_by_id(habit_id)

    def get_habits_for_user(self, user_id: str) -> List[Habit]:
        """Get all habits for a user."""
        return self.storage.get_habits_for_user(user_id)

    def get_user_habits(self, user_id: str) -> List[Habit]:
        """Alias for get_habits_for_user."""
        return self.get_habits_for_user(user_id)

    def get_all_habits(self) -> List[Habit]:
        """Get all habits (admin function)."""
        return self.storage.get_all_habits()

    def save_habit_direct(self, habit: Habit) -> bool:
        """Direct save to database."""
        return self.storage.save_habit(habit)

    def delete_habit(self, habit_id: str) -> bool:
        """Soft delete a habit."""
        if not habit_id:
            return False

        # ✅ Check if habit exists first
        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        # ✅ Check if already deleted
        if not habit.is_active:
            print(f"❌ Habit '{habit.name}' is already deleted")
            return False

        return self.storage.delete_habit(habit_id)

    def complete_habit(self, habit_id: str) -> bool:
        """Complete a habit (add a completion)."""
        if not habit_id:
            print("❌ Habit ID cannot be empty")
            return False

        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        # ✅ Check if habit is active
        if not habit.is_active:
            print(f"❌ Habit '{habit.name}' is deleted/archived")
            return False

        return self.storage.add_completion(habit_id)

    # ============================================
    # HABIT EDIT METHODS
    # ============================================

    def update_habit(self, habit: Habit) -> bool:
        """
        Update an existing habit.

        Args:
            habit: Habit object with updated fields

        Returns:
            bool: True if update was successful, False otherwise
        """
        return self.storage.update_habit(habit)

    def rename_habit(self, habit_id: str, new_name: str) -> bool:
        """
        Rename a habit.

        Args:
            habit_id: ID of the habit to rename
            new_name: New name for the habit

        Returns:
            bool: True if rename was successful, False otherwise
        """
        if not new_name or not new_name.strip():
            print("❌ Habit name cannot be empty")
            return False

        # Check if habit exists
        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        return self.storage.rename_habit(habit_id, new_name.strip())

    def update_habit_description(self, habit_id: str, new_description: str) -> bool:
        """
        Update a habit's description.

        Args:
            habit_id: ID of the habit to update
            new_description: New description for the habit

        Returns:
            bool: True if update was successful, False otherwise
        """
        # Check if habit exists
        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        return self.storage.update_habit_description(habit_id, new_description)

    def update_habit_periodicity(self, habit_id: str, new_periodicity: str) -> bool:
        """
        Update a habit's periodicity.

        Args:
            habit_id: ID of the habit to update
            new_periodicity: New periodicity ('daily', 'weekly', 'monthly')

        Returns:
            bool: True if update was successful, False otherwise
        """
        if new_periodicity not in ["daily", "weekly", "monthly"]:
            print(f"❌ Invalid periodicity: {new_periodicity}")
            return False

        # Check if habit exists
        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        # Update periodicity
        habit.periodicity = new_periodicity
        return self.storage.update_habit(habit)

    def edit_habit(
        self,
        habit_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        periodicity: Optional[str] = None,
    ) -> bool:
        """
        Edit a habit's details (name, description, periodicity).

        Args:
            habit_id: ID of the habit to edit
            name: New name (optional)
            description: New description (optional)
            periodicity: New periodicity (optional)

        Returns:
            bool: True if edit was successful, False otherwise
        """
        # Get the habit
        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        # Update fields if provided
        if name is not None and name.strip():
            habit.name = name.strip()

        if description is not None:
            habit.description = description

        if periodicity is not None:
            if periodicity not in ["daily", "weekly", "monthly"]:
                print(f"❌ Invalid periodicity: {periodicity}")
                return False
            habit.periodicity = periodicity

        # Save changes
        return self.storage.update_habit(habit)

    # ============================================
    # STREAK AND ANALYTICS
    # ============================================

    def get_habit_with_streak(self, habit_id: str) -> Dict[str, Any]:
        """
        Get a habit with its streak information.

        Args:
            habit_id: ID of the habit

        Returns:
            Dict containing habit data and streak information
        """
        habit = self.storage.get_habit_by_id(habit_id)
        if not habit:
            return {"error": "Habit not found"}

        # Use the analyzer instance
        streak_info = self.analyzer.get_streak_info(habit)

        return {
            "habit_id": habit.habit_id,
            "name": habit.name,
            "periodicity": habit.periodicity,
            "description": habit.description,
            "completions": len(habit.completions),
            "streak_info": streak_info,
        }

    def get_all_habits_with_streaks(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all habits for a user with streak information.

        Args:
            user_id: ID of the user

        Returns:
            List of dicts containing habit data and streak information
        """
        habits = self.storage.get_habits_for_user(user_id)
        result = []

        for habit in habits:
            # Use the analyzer instance
            streak_info = self.analyzer.get_streak_info(habit)
            result.append(
                {
                    "habit_id": habit.habit_id,
                    "name": habit.name,
                    "periodicity": habit.periodicity,
                    "description": habit.description,
                    "completions": len(habit.completions),
                    "streak_info": streak_info,
                }
            )

        return result

    def get_habit_streak_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all streaks for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dict containing summary statistics and habit details
        """
        habits = self.storage.get_habits_for_user(user_id)

        completed = 0
        in_progress = 0
        not_started = 0
        habit_summaries = []

        for habit in habits:
            # Use the analyzer instance
            streak_info = self.analyzer.get_streak_info(habit)

            if streak_info["is_complete"]:
                completed += 1
            elif streak_info["current"] > 0:
                in_progress += 1
            else:
                not_started += 1

            habit_summaries.append(
                {
                    "name": habit.name,
                    "periodicity": habit.periodicity,
                    "current": streak_info["current_display"],
                    "target": streak_info["target_display"],
                    "progress": streak_info["progress"],
                    "status": streak_info["status"],
                }
            )

        return {
            "total_habits": len(habits),
            "completed_streaks": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "habits": habit_summaries,
        }

    def get_longest_streak_habit(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the habit with the longest streak for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dict containing habit data and streak info, or None if no habits
        """
        habits = self.storage.get_habits_for_user(user_id)
        if not habits:
            return None

        # Use the analyzer to find the best habit
        best = self.analyzer.get_habit_with_longest_streak(habits)
        if best:
            return {
                "habit": best["habit"],
                "streak_info": best["streak_info"],
            }
        return None

    def get_habits_by_periodicity(self, user_id: str, periodicity: str) -> List[Habit]:
        """
        Get all habits for a user with a specific periodicity.

        Args:
            user_id: ID of the user
            periodicity: 'daily', 'weekly', or 'monthly'

        Returns:
            List of habits with the specified periodicity
        """
        all_habits = self.storage.get_habits_for_user(user_id)
        return self.analyzer.get_habits_by_periodicity(all_habits, periodicity)
