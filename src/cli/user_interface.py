# ruff: noqa: F821
# src/cli/user_interface.py

import os
import random
from datetime import datetime, timedelta

import questionary

from src.analytics.streak import StreakAnalyzer
from src.analytics.heatmap import HabitHeatmap
from src.core.database.repository import Storage
from src.core.models.user import User
from src.core.models.habit import Habit
from src.core.services.habit_service import HabitManager
from src.utils.predefined_habits import get_habits_by_periodicity


class UserInterface:
    """Command-line interface for the Habit Tracker application."""

    def __init__(self, storage=None):
        """
        Initialize the User Interface with database connection and habit manager.

        Args:
            storage: Optional Storage instance (for testing)
                    If None, creates production database connection.
        """
        # Ensure data directory exists
        data_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "data",
        )
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Initialize storage
        if storage is None:
            db_path = os.path.join(data_dir, "habits.db")
            self.storage = Storage(db_path)
        else:
            self.storage = storage

        # Initialize manager
        self.manager = HabitManager(self.storage)

        # Initialize StreakAnalyzer
        self.analyzer = StreakAnalyzer()

        # Initialize other attributes
        self.current_user = None
        self.running = True

    def run(self):
        """Main application loop - The entry point for the program."""
        while self.running:
            self._show_auth_menu()

            while self.current_user and self.running:
                self._show_main_menu()

    # ============================================
    # AUTHENTICATION MENUS
    # ============================================

    def _show_auth_menu(self):
        """Show the authentication menu using arrow keys."""
        all_users = self.manager.get_all_users()
        admin_exists = any(user.is_admin() for user in all_users)

        choices = [
            "🔑 Login",
            "📝 Register",
            "👤 Guest Login (Demo)",
        ]

        if not admin_exists:
            choices.append("🔑 Create First Admin")
        else:
            choices.append("👑 Admin Login")

        choices.append("🚪 Exit")

        choice = questionary.select(
            "🔐 What would you like to do?",
            choices=choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if choice == "🔑 Login":
            self._login()
        elif choice == "📝 Register":
            self._register()
        elif choice == "👤 Guest Login (Demo)":
            self._guest_login()
        elif choice == "👑 Admin Login":
            self._admin_login()
        elif choice == "🔑 Create First Admin":
            self._create_first_admin()
        elif choice == "🚪 Exit":
            print("\n👋 Goodbye!")
            self.running = False
            self.storage.close()

    # ============================================
    # MAIN MENUS
    # ============================================

    def _show_main_menu(self):
        """Display the main menu based on user role."""
        if self.current_user.role == "admin":
            self._show_admin_menu()
        elif self.current_user.role == "guest" or self.current_user.username == "guest":
            self._show_guest_menu()
        else:
            self._show_user_menu()

    def _show_user_menu(self):
        """Show the user menu with arrow keys."""
        choice = questionary.select(
            f"👤 Welcome, {self.current_user.username}! What would you like to do?",
            choices=[
                "📋 View My Habits",
                "➕ Create Habit",
                "✏️ Edit Habit",
                "✅ Complete Habit",
                "🗑️ Delete Habit",
                "📊 View Heatmap",
                "📈 View Dashboard",
                "🚪 Logout",
            ],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if choice == "📋 View My Habits":
            self._view_user_habits()
        elif choice == "➕ Create Habit":
            self._create_habit()
        elif choice == "✏️ Edit Habit":
            self._edit_habit()
        elif choice == "✅ Complete Habit":
            self._complete_habit()
        elif choice == "🗑️ Delete Habit":
            self._delete_habit()
        elif choice == "📊 View Heatmap":
            self._view_heatmap()
        elif choice == "📈 View Dashboard":
            self._show_user_dashboard()
        elif choice == "🚪 Logout":
            self._logout()

    def _show_guest_menu(self):
        """Display the menu for guest users (READ-ONLY)."""
        choice = questionary.select(
            "👤 GUEST MENU - Exploring Habit Tracker (READ-ONLY)",
            choices=[
                "📈 Guest Dashboard (Analytics)",
                "🔥 View Heatmap",
                "🔑 Login to Main Account",
                "🚪 Exit",
            ],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if choice == "📈 Guest Dashboard (Analytics)":
            self._show_guest_dashboard()
        elif choice == "🔥 View Heatmap":
            self._view_guest_heatmap()
        elif choice == "🔑 Login to Main Account":
            self._logout()
            self._login()
        elif choice == "🚪 Exit":
            self.running = False
            print("\n👋 Goodbye!")

    def _show_admin_menu(self):
        """Show the admin menu with arrow keys."""
        choice = questionary.select(
            f"👑 Admin Dashboard - {self.current_user.username}",
            choices=[
                "👥 View All Users",
                "📋 View All Habits",
                "📊 Admin Dashboard",
                "➕ Create New Admin Account",
                "🚪 Logout",
            ],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if choice == "👥 View All Users":
            self._view_all_users()
        elif choice == "📋 View All Habits":
            self._view_all_habits_admin()
        elif choice == "📊 Admin Dashboard":
            self._show_admin_dashboard()
        elif choice == "➕ Create New Admin Account":
            self._create_admin_account()
        elif choice == "🚪 Logout":
            self._logout()

    # ============================================
    # AUTHENTICATION METHODS
    # ============================================

    def _login(self):
        """Login a user."""
        username = questionary.text("Username:").ask()
        if not username:
            return

        password = questionary.password("Password:").ask()
        if not password:
            return

        user = self.manager.login_user(username, password)
        if user:
            self.current_user = user
            print(f"✅ Welcome back, {username}!")
        else:
            print("❌ Invalid username or password")

    def _register(self):
        """Register a new user."""
        username = questionary.text("Choose a username:").ask()
        if not username:
            return

        if self.manager.storage.username_exists(username):
            print(f"❌ Username '{username}' already exists")
            return

        email = questionary.text("Enter your email (optional):").ask()

        password = questionary.password("Choose a password:").ask()
        if not password:
            return

        confirm = questionary.password("Confirm password:").ask()
        if not confirm:
            return

        if password != confirm:
            print("❌ Passwords do not match")
            return

        user = self.manager.register_user(username, password, email)
        if user:
            self.current_user = user
            print(f"✅ Registration successful! Welcome, {username}!")
        else:
            print("❌ Registration failed")

    def _guest_login(self):
        """Login as guest with predefined habits."""
        print("\n👤 GUEST LOGIN")
        print("=" * 50)
        print("Username: guest")
        print("Password: guest123")
        print("=" * 50)

        username = questionary.text("Username:").ask()
        password = questionary.password("Password:").ask()

        if username != "guest" or password != "guest123":
            print("\n❌ Invalid guest credentials!")
            print("   Username: guest")
            print("   Password: guest123")
            return

        guest_id = "guest"

        if not self.storage.user_exists(guest_id):
            print("\n📋 Creating guest account...")
            guest_user = User(
                username="guest",
                email="",
                password="guest123",
                user_id=guest_id,
                role="guest",
            )
            self.storage.save_user(guest_user)
            print("✅ Guest account created!")

        habits = self.manager.get_habits_for_user(guest_id)

        if not habits:
            print("\n📋 Loading predefined habits with 4 weeks of test data...")

            try:
                from scripts.seed_data import PredefinedHabits

                demo_habits = PredefinedHabits.create(guest_id)
                print("   ✅ Loaded from seed_data.py")
            except (ImportError, AttributeError):
                print("   ⚠️ Using built-in habit generator...")
                demo_habits = self._create_guest_habits(guest_id)
                print("   ✅ Created with built-in generator")

            for habit in demo_habits:
                self.manager.save_habit_direct(habit)

            print(
                f"   ✅ Loaded {len(demo_habits)} guest habits with 4 weeks of test data!"
            )

        self.current_user = self.storage.get_user_by_id(guest_id)

        # noinspection PyUnresolvedReferences
        print(f"\n✅ Welcome, {self.current_user.username}!")
        print("   Role: Guest (User)")
        print("   Access: View predefined habits with 4-week test data")
        print("\n💡 Register to create your own habits!")

        input("\nPress Enter to continue...")

    def _create_admin_account(self):
        """Create a new admin account."""
        if not self.current_user or not self.current_user.is_admin():
            print("❌ Admin access required!")
            return

        print("\n" + "=" * 50)
        print("🔑 CREATE NEW ADMIN ACCOUNT")
        print("=" * 50)
        print("Create a new admin account with full system access.")
        print("⚠️  This action requires admin privileges.")
        print("=" * 50)

        username = questionary.text("Choose admin username:").ask()
        if not username or not username.strip():
            print("\n❌ Username cannot be empty!")
            return

        username = username.strip()

        if self.manager.storage.username_exists(username):
            print(f"\n❌ Username '{username}' already exists!")
            return

        email = questionary.text("Email (optional):").ask()

        password = questionary.password("Choose admin password:").ask()
        if not password or not password.strip():
            print("\n❌ Password cannot be empty!")
            return

        confirm = questionary.password("Confirm admin password:").ask()
        if password != confirm:
            print("\n❌ Passwords do not match!")
            return

        admin_user = self.manager.register_user(username, password, email, role="admin")

        if admin_user:
            print("\n✅ Admin account created successfully!")
            print(f"   Username: {username}")
            print("   Role: Administrator")
            print("\n📋 New admin can now login with their credentials.")
        else:
            print("\n❌ Failed to create admin account!")

        input("\nPress Enter to continue...")

    def _create_first_admin(self):
        """Create the first admin account."""
        print("\n" + "=" * 50)
        print("🔑 CREATE FIRST ADMIN ACCOUNT")
        print("=" * 50)
        print("This will create the first administrator account.")
        print("=" * 50)

        all_users = self.manager.get_all_users()
        if any(user.is_admin() for user in all_users):
            print("\n⚠️ Admin account already exists!")
            print("   Use 'Admin Login' to access the admin panel.")
            input("\nPress Enter to continue...")
            return

        # noinspection DuplicatedCode
        username = questionary.text("Choose admin username:").ask()
        if not username or not username.strip():
            print("\n❌ Username cannot be empty!")
            return

        username = username.strip()

        if self.manager.storage.username_exists(username):
            print(f"\n❌ Username '{username}' already exists!")
            return

        email = questionary.text("Email (optional):").ask()

        password = questionary.password("Choose admin password:").ask()
        if not password or not password.strip():
            print("\n❌ Password cannot be empty!")
            return

        confirm = questionary.password("Confirm admin password:").ask()
        if password != confirm:
            print("\n❌ Passwords do not match!")
            return

        admin_user = self.manager.register_user(username, password, email, role="admin")

        if admin_user:
            print("\n✅ Admin account created successfully!")
            print(f"   Username: {username}")
            print("   Role: Administrator")
            print("\n📋 You can now login with your admin credentials.")
        else:
            print("\n❌ Failed to create admin account!")

        input("\nPress Enter to continue...")

    def _admin_login(self):
        """Login as admin."""
        print("\n🔐 ADMIN LOGIN")
        print("=" * 50)

        all_users = self.manager.get_all_users()
        admin_exists = any(user.is_admin() for user in all_users)

        if not admin_exists:
            print("\n⚠️ No admin account found!")
            print("   Please create the first admin account:")
            print("   Select '🔑 Create First Admin'")
            print("=" * 50)
            input("\nPress Enter to continue...")
            return

        username = questionary.text("Admin username:").ask()
        if not username:
            return

        password = questionary.password("Admin password:").ask()
        if not password:
            return

        user = self.manager.login_user(username, password)
        if user and user.is_admin():
            self.current_user = user
            print("\n🔐 Admin login successful!")
            print(f"   Username: {username}")
            print("   Role: Administrator")
            print("   Access: Full system access")
        else:
            print("\n❌ Invalid admin credentials!")

    def _logout(self):
        """Logout the current user."""
        confirm = questionary.confirm("Are you sure you want to logout?").ask()
        if confirm:
            self.current_user = None
            print("✅ Logged out successfully")

    # ============================================
    # HABIT MANAGEMENT
    # ============================================

    def _view_user_habits(self):
        """View habits for the current user."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 You have no habits yet. Create one!")
            return

        print(f"\n📋 Your Habits ({len(habits)})")
        print("-" * 40)

        for i, habit in enumerate(habits, 1):
            streak_info = self.manager.get_habit_with_streak(habit.habit_id)
            status = "✅ Active" if habit.is_active else "❌ Inactive"

            print(f"{i}. {habit.name}")
            print(f"   Periodicity: {habit.periodicity}")
            print(f"   Completions: {len(habit.completions)}")
            print(f"   Status: {status}")

            if streak_info and "streak_info" in streak_info:
                si = streak_info["streak_info"]
                print(f"   Current Streak: {si.get('current_display', 'N/A')}")
                print(f"   Best Streak: {si.get('longest_display', 'N/A')}")

            print()

        questionary.press_any_key_to_continue().ask()

    def _create_habit(self):
        """Create a new habit using predefined templates or custom."""
        if not self.current_user:
            print("❌ Please login first")
            return

        choice = questionary.select(
            "📋 How would you like to create your habit?",
            choices=[
                "📝 Choose from predefined templates",
                "✏️ Create custom habit",
                "🔙 Cancel",
            ],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if choice == "📝 Choose from predefined templates":
            self._create_habit_with_template()
        elif choice == "✏️ Create custom habit":
            self._create_custom_habit()
        else:
            print("❌ Cancelled")

    def _create_habit_with_template(self):
        """Create a habit using predefined templates."""
        try:
            period = questionary.select(
                "📋 Select habit type:",
                choices=[
                    "🌅 Daily habits (3)",
                    "📅 Weekly habits (2)",
                    "📆 Monthly habits (2)",
                    "🔙 Cancel",
                ],
                style=questionary.Style(
                    [
                        ("selected", "fg:cyan bold"),
                        ("pointer", "fg:cyan bold"),
                        ("highlighted", "fg:cyan"),
                    ]
                ),
            ).ask()

            if period == "🔙 Cancel":
                return

            period_map = {
                "🌅 Daily habits (3)": "daily",
                "📅 Weekly habits (2)": "weekly",
                "📆 Monthly habits (2)": "monthly",
            }
            periodicity = period_map.get(period)

            if not periodicity:
                return

            templates = get_habits_by_periodicity(periodicity)

            choices = []
            for template in templates:
                choices.append(f"{template['name']} - {template['description']}")
            choices.append("🔙 Cancel")

            selected = questionary.select(
                f"📋 Available {periodicity} habits:",
                choices=choices,
                style=questionary.Style(
                    [
                        ("selected", "fg:cyan bold"),
                        ("pointer", "fg:cyan bold"),
                        ("highlighted", "fg:cyan"),
                    ]
                ),
            ).ask()

            if selected == "🔙 Cancel" or not selected:
                return

            idx = choices.index(selected)
            if idx >= len(templates):
                return

            template = templates[idx]

            print("\n✅ Creating habit:")
            print(f"  Name: {template['name']}")
            print(f"  Description: {template['description']}")
            print(f"  Periodicity: {template['periodicity']}")

            confirm = questionary.confirm("Confirm?").ask()

            if confirm:
                habit = self.manager.create_habit(
                    name=template["name"],
                    periodicity=template["periodicity"],
                    user_id=self.current_user.user_id,
                    description=template["description"],
                )

                if habit:
                    print(f"✅ Habit '{template['name']}' created successfully!")
                else:
                    print("❌ Failed to create habit")

        except Exception as e:
            print(f"❌ Error creating habit: {e}")

    def _create_custom_habit(self):
        """Create a custom habit from scratch."""
        try:
            name = questionary.text("Enter habit name:").ask()
            if not name:
                print("❌ Habit name cannot be empty")
                return

            description = questionary.text("Enter description (optional):").ask()

            periodicity = questionary.select(
                "Select periodicity:",
                choices=["🌅 Daily", "📅 Weekly", "📆 Monthly"],
                style=questionary.Style(
                    [
                        ("selected", "fg:cyan bold"),
                        ("pointer", "fg:cyan bold"),
                        ("highlighted", "fg:cyan"),
                    ]
                ),
            ).ask()

            period_map = {
                "🌅 Daily": "daily",
                "📅 Weekly": "weekly",
                "📆 Monthly": "monthly",
            }
            period = period_map.get(periodicity)

            if not period:
                print("❌ Invalid periodicity")
                return

            habit = self.manager.create_habit(
                name=name,
                periodicity=period,
                user_id=self.current_user.user_id,
                description=description,
            )

            if habit:
                print(f"✅ Habit '{name}' created successfully!")
            else:
                print("❌ Failed to create habit")

        except Exception as e:
            print(f"❌ Error creating habit: {e}")

    # noinspection PyMethodMayBeStatic
    def _create_guest_habits(self, user_id: str) -> list:
        """Create guest habits directly (fallback method)."""
        habits = []
        random.seed(42)

        now = datetime.now()
        start_date = (now - timedelta(days=27)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # DAILY HABIT 1: PERFECT (28/28 days)
        h = Habit(
            name="Morning Exercise",
            user_id=user_id,
            description="30 minutes of physical activity",
            periodicity="daily",
        )
        for day in range(28):
            h.complete(start_date + timedelta(days=day))
        habits.append(h)

        # DAILY HABIT 2: STRUGGLING (11/28 days)
        h = Habit(
            name="Drink Water",
            user_id=user_id,
            description="Drink 8 glasses of water daily",
            periodicity="daily",
        )
        for day in [0, 1, 2, 5, 6, 10, 14, 15, 16, 20, 25]:
            h.complete(start_date + timedelta(days=day))
        habits.append(h)

        # DAILY HABIT 3: IN PROGRESS (20/28 days)
        h = Habit(
            name="Read Books",
            user_id=user_id,
            description="Read for 20 minutes daily",
            periodicity="daily",
        )
        for day in [
            0,
            1,
            2,
            3,
            4,
            5,
            10,
            11,
            12,
            13,
            14,
            15,
            18,
            19,
            20,
            21,
            22,
            23,
            25,
            26,
        ]:
            h.complete(start_date + timedelta(days=day))
        habits.append(h)

        # WEEKLY HABIT: PERFECT (4/4 weeks)
        h = Habit(
            name="Weekly Review",
            user_id=user_id,
            description="Review goals and plan the week",
            periodicity="weekly",
        )
        for week in range(4):
            h.complete(start_date + timedelta(weeks=week))
        habits.append(h)

        # WEEKLY HABIT: STRUGGLING (1/4 weeks)
        h = Habit(
            name="Clean House",
            user_id=user_id,
            description="Thorough house cleaning",
            periodicity="weekly",
        )
        h.complete(start_date + timedelta(weeks=2))
        habits.append(h)

        # MONTHLY HABIT: IN PROGRESS (3/4 months)
        h = Habit(
            name="Financial Check",
            user_id=user_id,
            description="Review budget and finances",
            periodicity="monthly",
        )  # noqa: F821
        for month in [0, 1, 3]:
            h.complete(start_date + timedelta(days=30 * month))
        habits.append(h)

        # MONTHLY HABIT: STRUGGLING (1/4 months)
        h = Habit(
            name="Skill Development",
            user_id=user_id,
            description="Complete a course or learn a skill",
            periodicity="monthly",
        )
        h.complete(start_date)
        habits.append(h)

        return habits

    def _complete_habit(self):
        """Complete a habit."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 You have no habits to complete")
            return

        choices = []
        for habit in habits:
            choices.append(f"{habit.name} ({habit.periodicity})")
        choices.append("🔙 Cancel")

        selected = questionary.select(
            "Select habit to complete:",
            choices=choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if selected == "🔙 Cancel" or not selected:
            return

        idx = choices.index(selected)
        if idx >= len(habits):
            return

        habit = habits[idx]

        confirm = questionary.confirm(f"Complete '{habit.name}'?").ask()

        if confirm:
            if self.manager.complete_habit(habit.habit_id):
                print(f"✅ Completed '{habit.name}'!")
            else:
                print("❌ Failed to complete habit")

    def _delete_habit(self):
        """Delete a habit."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 You have no habits to delete")
            return

        choices = []
        for habit in habits:
            choices.append(f"{habit.name} ({habit.periodicity})")
        choices.append("🔙 Cancel")

        selected = questionary.select(
            "Select habit to delete:",
            choices=choices,
            style=questionary.Style(
                [
                    ("selected", "fg:red bold"),
                    ("pointer", "fg:red bold"),
                    ("highlighted", "fg:red"),
                ]
            ),
        ).ask()

        if selected == "🔙 Cancel" or not selected:
            return

        idx = choices.index(selected)
        if idx >= len(habits):
            return

        habit = habits[idx]

        confirm = questionary.confirm(
            f"⚠️  Delete '{habit.name}'? This action cannot be undone!", default=False
        ).ask()

        if confirm:
            if self.manager.delete_habit(habit.habit_id):
                print(f"✅ Deleted '{habit.name}'")
            else:
                print("❌ Failed to delete habit")

    def _edit_habit(self):
        """Edit an existing habit."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 You have no habits to edit")
            input("\nPress Enter to continue...")
            return

        # Select habit to edit
        choices = []
        for habit in habits:
            choices.append(f"{habit.name} ({habit.periodicity})")
        choices.append("🔙 Cancel")

        selected = questionary.select(
            "✏️ Select habit to edit:",
            choices=choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if selected == "🔙 Cancel" or not selected:
            return

        idx = choices.index(selected)
        if idx >= len(habits):
            return

        habit = habits[idx]

        print("\n" + "=" * 50)
        print(f"✏️ EDITING: {habit.name}")
        print("=" * 50)
        print(f"Current name: {habit.name}")
        print(
            f"Current description: {habit.description if habit.description else '(none)'}"
        )
        print(f"Current periodicity: {habit.periodicity}")
        print("=" * 50)

        # Show edit options
        edit_choice = questionary.select(
            "What would you like to edit?",
            choices=[
                "📝 Rename Habit",
                "📄 Edit Description",
                "📅 Change Periodicity",
                "✏️ Edit All Fields",
                "🔙 Cancel",
            ],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if edit_choice == "🔙 Cancel" or not edit_choice:
            return

        if edit_choice == "📝 Rename Habit":
            self._rename_habit(habit)
        elif edit_choice == "📄 Edit Description":
            self._edit_habit_description(habit)
        elif edit_choice == "📅 Change Periodicity":
            self._change_habit_periodicity(habit)
        elif edit_choice == "✏️ Edit All Fields":
            self._edit_all_habit_fields(habit)

    def _rename_habit(self, habit: Habit):
        """Rename a habit."""
        print(f"\n📝 Renaming: {habit.name}")
        print("=" * 40)

        new_name = questionary.text("Enter new name:").ask()
        if not new_name or not new_name.strip():
            print("❌ Habit name cannot be empty")
            return

        confirm = questionary.confirm(
            f"Rename '{habit.name}' to '{new_name.strip()}'?"
        ).ask()

        if confirm:
            if self.manager.rename_habit(habit.habit_id, new_name.strip()):
                print(f"✅ Habit renamed to '{new_name.strip()}'!")
            else:
                print("❌ Failed to rename habit")

        input("\nPress Enter to continue...")

    def _edit_habit_description(self, habit: Habit):
        """Edit a habit's description."""
        print(f"\n📄 Editing description for: {habit.name}")
        print("=" * 40)
        print(
            f"Current description: {habit.description if habit.description else '(none)'}"
        )
        print("=" * 40)

        new_description = questionary.text(
            "Enter new description (or leave empty to clear):"
        ).ask()

        if new_description is None:
            return

        confirm = questionary.confirm("Update description?").ask()

        if confirm:
            if self.manager.update_habit_description(habit.habit_id, new_description):
                print("✅ Description updated!")
            else:
                print("❌ Failed to update description")

        input("\nPress Enter to continue...")

    def _change_habit_periodicity(self, habit: Habit):
        """Change a habit's periodicity."""
        print(f"\n📅 Changing periodicity for: {habit.name}")
        print("=" * 40)
        print(f"Current periodicity: {habit.periodicity}")
        print("=" * 40)

        new_periodicity = questionary.select(
            "Select new periodicity:",
            choices=["🌅 Daily", "📅 Weekly", "📆 Monthly"],
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if not new_periodicity:
            return

        period_map = {
            "🌅 Daily": "daily",
            "📅 Weekly": "weekly",
            "📆 Monthly": "monthly",
        }
        new_period = period_map.get(new_periodicity)

        if not new_period:
            return

        confirm = questionary.confirm(
            f"Change periodicity from '{habit.periodicity}' to '{new_period}'?"
        ).ask()

        if confirm:
            if self.manager.update_habit_periodicity(habit.habit_id, new_period):
                print(f"✅ Periodicity changed to '{new_period}'!")
            else:
                print("❌ Failed to change periodicity")

        input("\nPress Enter to continue...")

    def _edit_all_habit_fields(self, habit: Habit):
        """Edit all fields of a habit."""
        print(f"\n✏️ EDITING ALL FIELDS: {habit.name}")
        print("=" * 50)

        # Edit name
        new_name = questionary.text(
            f"Name (current: {habit.name}):", default=habit.name
        ).ask()

        if not new_name or not new_name.strip():
            print("❌ Habit name cannot be empty")
            return

        # Edit description
        new_description = questionary.text(
            f"Description (current: {habit.description if habit.description else 'none'}):",
            default=habit.description if habit.description else "",
        ).ask()

        # Edit periodicity
        choices = []
        for p in ["daily", "weekly", "monthly"]:
            label = p.capitalize()
            if p == habit.periodicity:
                label += " (current)"
            choices.append(label)

        period_choice = questionary.select(
            f"Periodicity (current: {habit.periodicity}):",
            choices=choices,
        ).ask()

        if not period_choice:
            return

        period_map = {
            "Daily (current)": "daily",
            "Daily": "daily",
            "Weekly (current)": "weekly",
            "Weekly": "weekly",
            "Monthly (current)": "monthly",
            "Monthly": "monthly",
        }
        new_period = period_map.get(period_choice, habit.periodicity)

        print("\n" + "=" * 50)
        print("📋 SUMMARY OF CHANGES:")
        print(f"  Name: {habit.name} → {new_name.strip()}")
        print(
            f"  Description: {habit.description if habit.description else 'none'} → {new_description if new_description else 'none'}"
        )
        print(f"  Periodicity: {habit.periodicity} → {new_period}")
        print("=" * 50)

        confirm = questionary.confirm("Apply these changes?").ask()

        if confirm:
            success = self.manager.edit_habit(
                habit_id=habit.habit_id,
                name=new_name.strip(),
                description=new_description,
                periodicity=new_period,
            )

            if success:
                print("✅ Habit updated successfully!")
            else:
                print("❌ Failed to update habit")

        input("\nPress Enter to continue...")

    # ============================================
    # DASHBOARD AND ANALYTICS
    # ============================================

    def _view_heatmap(self):
        """View the heatmap for the current user."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 No habits to display")
            questionary.press_any_key_to_continue().ask()
            return

        if len(habits) > 1:
            choices = []
            for habit in habits:
                choices.append(f"{habit.name} ({habit.periodicity})")
            choices.append("🔙 Cancel")

            selected = questionary.select(
                "Select habit for heatmap:",
                choices=choices,
            ).ask()

            if selected == "🔙 Cancel" or not selected:
                return

            idx = choices.index(selected)
            if idx >= len(habits):
                return

            habit = habits[idx]
        else:
            habit = habits[0]

        heatmap = HabitHeatmap(habit)
        result = heatmap.show()
        print(result)

        questionary.press_any_key_to_continue().ask()

    def _view_guest_heatmap(self):
        """View heatmap for guest habits (READ-ONLY)."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 No guest habits to display")
            questionary.press_any_key_to_continue().ask()
            return

        choices = []
        for habit in habits:
            choices.append(f"{habit.name} ({habit.periodicity})")
        choices.append("🔙 Cancel")

        selected = questionary.select(
            "📊 Select habit for heatmap:",
            choices=choices,
        ).ask()

        if selected == "🔙 Cancel" or not selected:
            return

        idx = choices.index(selected)
        if idx >= len(habits):
            return

        habit = habits[idx]

        heatmap = HabitHeatmap(habit)
        result = heatmap.show()
        print(result)

        print("💡 Register to create your own habits!")
        questionary.press_any_key_to_continue().ask()

    def _show_user_dashboard(self):
        """Show the user dashboard with full analytics."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("\n📭 No habits found!")
            print("   Create your first habit to see analytics!")
            input("\nPress Enter to continue...")
            return

        print("\n" + "=" * 70)
        print(f"📊 MY DASHBOARD - {self.current_user.username}")
        print("=" * 70)

        daily = [h for h in habits if h.periodicity == "daily"]
        weekly = [h for h in habits if h.periodicity == "weekly"]
        monthly = [h for h in habits if h.periodicity == "monthly"]

        if daily:
            print(f"\n📆 DAILY HABITS ({len(daily)}) - Target: 28 days")
            print("-" * 60)
            for habit in daily:
                self._display_habit_streak(habit)

        if weekly:
            print(f"\n📅 WEEKLY HABITS ({len(weekly)}) - Target: 4 weeks")
            print("-" * 60)
            for habit in weekly:
                self._display_habit_streak(habit)

        if monthly:
            print(f"\n📅 MONTHLY HABITS ({len(monthly)}) - Target: 4 months")
            print("-" * 60)
            for habit in monthly:
                self._display_habit_streak(habit)

        print("\n" + "=" * 70)
        print("📈 OVERALL STATISTICS")
        print("-" * 60)
        total_completions = sum(len(h.completions) for h in habits)
        print(f"   Total Habits: {len(habits)}")
        print(f"   Total Completions: {total_completions}")

        best_habit = None
        best_streak = 0
        for habit in habits:
            streak_info = self.manager.get_habit_with_streak(habit.habit_id)
            if streak_info and "streak_info" in streak_info:
                current = streak_info["streak_info"].get("current", 0)
                if current > best_streak:
                    best_streak = current
                    best_habit = habit

        if best_habit:
            print(f"   🏆 Best Streak: {best_streak} days - {best_habit.name}")

        print("\n" + "=" * 70)
        input("\nPress Enter to continue...")

    def _display_habit_streak(self, habit):
        """Display a single habit's streak information."""
        streak_info = self.manager.get_habit_with_streak(habit.habit_id)

        print(f"\n   ✅ {habit.name}")
        if habit.description and habit.description.strip():
            print(f"      📝 {habit.description}")
        print(f"      📅 Periodicity: {habit.periodicity.capitalize()}")
        print(f"      ✅ Completions: {len(habit.completions)}")

        if streak_info and "streak_info" in streak_info:
            si = streak_info["streak_info"]
            print(f"      🔥 Current Streak: {si.get('current_display', 'N/A')}")
            print(f"      🏆 Best Streak: {si.get('longest_display', 'N/A')}")
            print(f"      🎯 Target: {si.get('target_display', 'N/A')}")
            print(f"      📊 Progress: {si.get('progress_display', 'N/A')}")

            if "progress" in si:
                bar = self.analyzer.create_progress_bar(si["progress"])
                print(f"      {bar}")

            print(f"      📈 Status: {si.get('status', 'N/A')}")

            if si.get("milestone_msg"):
                print(f"      💬 {si['milestone_msg']}")

    def _show_guest_dashboard(self):
        """Show comprehensive guest dashboard with analytics menu."""
        habits = self.manager.get_habits_for_user("guest")

        if not habits:
            print("\n📭 No guest habits found!")
            input("\nPress Enter to continue...")
            return

        while True:
            print("\n" + "=" * 70)
            print("👤 GUEST DASHBOARD - Analytics Menu")
            print("=" * 70)
            print("📊 4-WEEK TEST DATA WITH VARYING COMPLETION PATTERNS")
            print("💡 Register to create your own habits!")
            print("=" * 70)

            choice = questionary.select(
                "Select what to view:",
                choices=[
                    "1. View All Current Tracked Habits",
                    "2. Habits With The Same Periodicity",
                    "3. Struggling habits",
                    "4. Longest Streak For Specific Habits",
                    "5. Longest Streak (all habits)",
                    "🔙 Back to Guest Menu",
                ],
            ).ask()

            if choice == "🔙 Back to Guest Menu":
                return

            if choice == "1. View All Current Tracked Habits":
                self._display_all_guest_habits(habits)
                input("\nPress Enter to continue...")
            elif choice == "2. Habits With The Same Periodicity":
                self._display_habits_by_periodicity_menu(habits)
            elif choice == "3. Struggling habits":
                self._display_struggling_habits(habits)
            elif choice == "4. Longest Streak For Specific Habits":
                self._display_longest_streaks_for_habits(habits)
            elif choice == "5. Longest Streak (all habits)":
                self._display_longest_streak_all_habits(habits)

    # ============================================================
    # GUEST DASHBOARD HELPER METHODS
    # ============================================================

    def _display_all_guest_habits(self, habits):
        """Display all guest habits with detailed information (READ-ONLY)."""
        if not habits:
            print("\n📭 No habits to display!")
            input("\nPress Enter to continue...")
            return

        print("\n" + "=" * 70)
        print(f"📊 ALL GUEST HABITS ({len(habits)} habits)")
        print("=" * 70)
        print("4-WEEK TEST DATA WITH REALISTIC PATTERNS")
        print("=" * 70)

        daily = [h for h in habits if h.periodicity == "daily"]
        weekly = [h for h in habits if h.periodicity == "weekly"]
        monthly = [h for h in habits if h.periodicity == "monthly"]

        if daily:
            print(f"\n📆 DAILY HABITS ({len(daily)}) - Target: 28 days")
            print("-" * 60)
            for i, habit in enumerate(daily, 1):
                self._display_habit_summary(habit, i)

        if weekly:
            print(f"\n📅 WEEKLY HABITS ({len(weekly)}) - Target: 4 weeks")
            print("-" * 60)
            for i, habit in enumerate(weekly, 1):
                self._display_habit_summary(habit, i)

        if monthly:
            print(f"\n📅 MONTHLY HABITS ({len(monthly)}) - Target: 4 months")
            print("-" * 60)
            for i, habit in enumerate(monthly, 1):
                self._display_habit_summary(habit, i)

        print("\n" + "=" * 70)
        print("💡 Register to create your own habits!")
        input("\nPress Enter to continue...")

    def _display_habit_summary(self, habit, index):
        """Display a single habit summary."""
        streak_info = self.manager.get_habit_with_streak(habit.habit_id)

        print(f"\n{index}. {habit.name}")
        if habit.description and habit.description.strip():
            print(f"   📝 {habit.description}")
        print(f"   ✅ Completions: {len(habit.completions)}")
        print(f"   📅 Periodicity: {habit.periodicity.capitalize()}")

        # noinspection DuplicatedCode
        if streak_info and "streak_info" in streak_info:
            si = streak_info["streak_info"]
            print(f"   🔥 Current Streak: {si.get('current_display', 'N/A')}")
            print(f"   🏆 Best Streak: {si.get('longest_display', 'N/A')}")
            print(f"   🎯 Target: {si.get('target_display', 'N/A')}")
            print(f"   📊 Progress: {si.get('progress_display', 'N/A')}")

            if "progress" in si:
                bar = self.analyzer.create_progress_bar(si["progress"])
                print(f"   {bar}")

            print(f"   📈 Status: {si.get('status', 'N/A')}")

            if si.get("milestone_msg"):
                print(f"   💬 {si['milestone_msg']}")

    def _display_habits_by_periodicity_menu(self, habits):
        """Display habits grouped by periodicity with a submenu."""
        if not habits:
            print("\n📭 No habits to display!")
            input("\nPress Enter to continue...")
            return

        while True:
            print("\n" + "=" * 70)
            print("📊 HABITS WITH THE SAME PERIODICITY")
            print("=" * 70)

            # noinspection SpellCheckingInspection
            periodicities = sorted(set(h.periodicity for h in habits))
            choices = [f"📆 {p.capitalize()} Habits" for p in periodicities]
            choices.append("🔙 Back to Dashboard Menu")

            choice = questionary.select(
                "Select periodicity to view:", choices=choices
            ).ask()

            if choice == "🔙 Back to Dashboard Menu":
                return

            idx = choices.index(choice)
            if idx >= len(periodicities):
                continue

            periodicity = periodicities[idx]
            filtered = [h for h in habits if h.periodicity == periodicity]

            if filtered:
                self._display_habits_with_streaks(
                    filtered, f"{periodicity.capitalize()} HABITS"
                )
            else:
                print(f"\n📭 No {periodicity} habits found!")
                input("\nPress Enter to continue...")

    def _display_habits_with_streaks(self, habits, title):
        """Display habits with streak information (READ-ONLY)."""
        print(f"\n📊 {title} ({len(habits)} habits)")
        print("=" * 60)

        for i, habit in enumerate(habits, 1):
            streak_info = self.manager.get_habit_with_streak(habit.habit_id)

            print(f"\n{i}. {habit.name}")
            if habit.description and habit.description.strip():
                print(f"   📝 {habit.description}")
            print(f"   📅 Periodicity: {habit.periodicity.capitalize()}")
            print(f"   ✅ Completions: {len(habit.completions)}")

            if streak_info and "streak_info" in streak_info:
                si = streak_info["streak_info"]
                print(f"   🔥 Streak: {si.get('current_display', 'N/A')}")
                print(f"   🎯 Target: {si.get('target_display', 'N/A')}")
                print(f"   📊 Progress: {si.get('progress_display', 'N/A')}")
                print(f"   📈 Status: {si.get('status', 'N/A')}")

                if "progress" in si:
                    bar = self.analyzer.create_progress_bar(si["progress"])
                    print(f"   {bar}")

                if si.get("milestone_msg"):
                    print(f"   💬 {si['milestone_msg']}")

        print("\n" + "=" * 60)
        input("\nPress Enter to continue...")

    def _display_struggling_habits(self, habits):
        """Display struggling habits (less than 50% completion rate)."""
        print("\n" + "=" * 70)
        print("⚠️ STRUGGLING HABITS (Less than 50% completion)")
        print("=" * 70)
        print("Habits with less than 50% completion rate")
        print("=" * 70)

        struggling = []
        for habit in habits:
            completions = len(habit.completions)
            if habit.periodicity == "daily":
                total_possible = 28
            elif habit.periodicity == "weekly":
                total_possible = 4
            else:
                total_possible = 4

            rate = (completions / total_possible) * 100 if total_possible > 0 else 0
            if rate < 50:
                struggling.append((habit, rate))

        if struggling:
            struggling.sort(key=lambda x: x[1])

            for habit, rate in struggling:
                streak_info = self.manager.get_habit_with_streak(habit.habit_id)

                print(f"\n   ⚠️ {habit.name}")
                if habit.description and habit.description.strip():
                    print(f"      📝 {habit.description}")
                print(f"      📅 Periodicity: {habit.periodicity.capitalize()}")
                print(f"      📊 Completion Rate: {rate:.0f}%")

                if streak_info and "streak_info" in streak_info:
                    si = streak_info["streak_info"]
                    print(
                        f"      🔥 Current Streak: {si.get('current_display', 'N/A')}"
                    )
                    # noinspection PyUnboundLocalVariable
                    print(
                        f"      ✅ Total Completions: {len(habit.completions)} out of {total_possible} possible"
                    )
                    print("      💪 Tip: Try to complete this habit more consistently!")

        else:
            print("\n   🎉 No struggling habits! All habits are above 50% completion!")
            print("   Keep up the great work! 💪")

        print("\n" + "=" * 70)
        input("\nPress Enter to continue...")

    def _display_longest_streaks_for_habits(self, habits):
        """Display the longest streak for each habit."""
        if not habits:
            print("\n📭 No habits to display!")
            input("\nPress Enter to continue...")
            return

        print("\n" + "=" * 70)
        print("🏆 LONGEST STREAK FOR EACH HABIT")
        print("=" * 70)

        for habit in habits:
            streak_info = self.manager.get_habit_with_streak(habit.habit_id)

            print(f"\n   📌 {habit.name}")
            if habit.description and habit.description.strip():
                print(f"      📝 {habit.description}")

            if streak_info and "streak_info" in streak_info:
                si = streak_info["streak_info"]
                print(f"      🔥 Current Streak: {si.get('current_display', 'N/A')}")
                print(f"      🏆 Longest Streak: {si.get('longest_display', 'N/A')}")
                print(f"      📊 Progress: {si.get('progress_display', 'N/A')}")
                print(f"      ✅ Total Completions: {len(habit.completions)}")

                if si.get("milestone_msg"):
                    print(f"      💬 {si['milestone_msg']}")

            print()

        print("=" * 70)
        input("\nPress Enter to continue...")

    def _display_longest_streak_all_habits(self, habits):
        """Display the habit with the longest streak across all habits."""
        print("\n" + "=" * 70)
        print("🏆 LONGEST STREAK (ALL HABITS)")
        print("=" * 70)

        if not habits:
            print("\n   📭 No habits to display!")
            input("\nPress Enter to continue...")
            return

        best_habit = None
        best_streak = 0
        best_info = None

        for habit in habits:
            streak_info = self.manager.get_habit_with_streak(habit.habit_id)
            if streak_info and "streak_info" in streak_info:
                si = streak_info["streak_info"]
                current = si.get("current", 0)
                periodicity = habit.periodicity
                if periodicity == "daily":
                    streak_in_days = current
                elif periodicity == "weekly":
                    streak_in_days = current * 7
                elif periodicity == "monthly":
                    streak_in_days = current * 30
                else:
                    streak_in_days = current

                if streak_in_days > best_streak:
                    best_streak = streak_in_days
                    best_habit = habit
                    best_info = si

        if best_habit and best_info:
            bar = self.analyzer.create_progress_bar(best_info.get("progress", 0))

            print(f"\n   🏆 Winner: {best_habit.name}")
            if best_habit.description and best_habit.description.strip():
                print(f"      📝 {best_habit.description}")
            print(f"      📅 Periodicity: {best_habit.periodicity.capitalize()}")
            print(f"      🔥 Streak: {best_info.get('current_display', 'N/A')}")
            print(f"      📊 Progress: {best_info.get('progress_display', 'N/A')}")
            print(f"      {bar}")
            print(f"      ✅ Total Completions: {len(best_habit.completions)}")
            print(f"      📈 Status: {best_info.get('status', 'N/A')}")

            if best_info.get("milestone_msg"):
                # noinspection PyUnresolvedReferences
                print(f"      💬 {best_info['milestone_msg']}")

            print("\n" + "=" * 70)
            print("📊 HOW OTHER HABITS COMPARE")
            print("=" * 70)
            for habit in habits:
                if habit.habit_id != best_habit.habit_id:
                    streak_info = self.manager.get_habit_with_streak(habit.habit_id)
                    if streak_info and "streak_info" in streak_info:
                        si = streak_info["streak_info"]
                        print(f"   • {habit.name}: {si.get('current_display', 'N/A')}")
        else:
            print("\n   📭 No completions recorded yet!")
            print("   💪 Start completing your habits to build streaks!")

        print("\n" + "=" * 70)
        input("\nPress Enter to continue...")

    # ============================================
    # ADMIN METHODS
    # ============================================

    def _view_all_users(self):
        """View all users (admin only)."""
        if not self.current_user or not self.current_user.is_admin():
            print("❌ Admin access required")
            return

        users = self.manager.get_all_users()

        print(f"\n👥 All Users ({len(users)})")
        print("-" * 40)

        for user in users:
            status = "🟢 Active" if user.is_active else "🔴 Inactive"
            role = "👑 Admin" if user.is_admin() else "👤 User"
            print(f"  {user.username} - {role} - {status}")

        questionary.press_any_key_to_continue().ask()

    def _view_all_habits_admin(self):
        """View all habits (admin only)."""
        if not self.current_user or not self.current_user.is_admin():
            print("❌ Admin access required")
            return

        habits = self.manager.get_all_habits()

        print(f"\n📋 All Habits ({len(habits)})")
        print("-" * 40)

        for habit in habits:
            user = self.manager.get_user_by_id(habit.user_id)
            username = user.username if user else "Unknown"
            print(f"  {habit.name} - {username} ({habit.periodicity})")

        questionary.press_any_key_to_continue().ask()

    def _show_admin_dashboard(self):
        """Show the admin dashboard."""
        if not self.current_user or not self.current_user.is_admin():
            print("❌ Admin access required")
            return

        users = self.manager.get_all_users()
        habits = self.manager.get_all_habits()

        print("\n👑 ADMIN DASHBOARD")
        print("-" * 40)
        print(f"  Total Users: {len(users)}")
        print(f"  Total Habits: {len(habits)}")
        print(f"  Active Users: {len([u for u in users if u.is_active])}")

        questionary.press_any_key_to_continue().ask()

    def _filter_guest_habits_by_periodicity(self):
        """Filter and display guest habits by periodicity (READ-ONLY)."""
        if not self.current_user:
            print("❌ Please login first")
            return

        habits = self.manager.get_habits_for_user(self.current_user.user_id)

        if not habits:
            print("📭 No guest habits found!")
            return

        periodicities = sorted(set(h.periodicity for h in habits))
        choices = [f"📆 {p.capitalize()}" for p in periodicities]
        choices.append("🔙 Cancel")

        selected = questionary.select(
            "📊 Select periodicity to filter:",
            choices=choices,
            style=questionary.Style(
                [
                    ("selected", "fg:cyan bold"),
                    ("pointer", "fg:cyan bold"),
                    ("highlighted", "fg:cyan"),
                ]
            ),
        ).ask()

        if selected == "🔙 Cancel" or not selected:
            return

        idx = choices.index(selected)
        if idx >= len(periodicities):
            return

        periodicity = periodicities[idx]

        filtered = [h for h in habits if h.periodicity == periodicity]

        print(f"\n📊 {periodicity.capitalize()} Habits ({len(filtered)}) - READ ONLY")
        print("=" * 60)

        for i, habit in enumerate(filtered, 1):
            streak_info = self.manager.get_habit_with_streak(habit.habit_id)

            print(f"\n{i}. {habit.name}")
            if habit.description and habit.description.strip():
                print(f"   📝 {habit.description}")
            print(f"   ✅ Completions: {len(habit.completions)}")

            if streak_info and "streak_info" in streak_info:
                si = streak_info["streak_info"]
                print(f"   🔥 Streak: {si.get('current_display', 'N/A')}")
                print(f"   📊 Progress: {si.get('progress_display', 'N/A')}")

            print()

        print("=" * 60)
        print("💡 Register to create your own habits!")
        questionary.press_any_key_to_continue().ask()
