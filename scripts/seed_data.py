# ruff: noqa: E402
# scripts/seed_data.py

"""
SEED DATA GENERATOR - Creates test data for the Habit Tracker.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import random
import uuid
from datetime import datetime, timedelta  # noqa: E402

from src.core.database.repository import Storage
from src.core.models.habit import Habit
from src.core.models.user import User


# ✅ Define get_db_path directly
def get_db_path() -> str:
    """Get the database file path."""
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    return str(data_dir / "habits.db")


# ============================================
# HABIT TEMPLATES
# ============================================

DAILY_HABITS = [
    {
        "name": "Morning Exercise",
        "description": "30 minutes of physical activity",
        "periodicity": "daily",
        "pattern": "perfect",
    },
    {
        "name": "Read Daily",
        "description": "Read 20 pages of a book",
        "periodicity": "daily",
        "pattern": "struggling",
    },
    {
        "name": "Meditate",
        "description": "10 minutes of mindfulness meditation",
        "periodicity": "daily",
        "pattern": "in_progress",
    },
]

WEEKLY_HABITS = [
    {
        "name": "Weekly Review",
        "description": "Plan and review the week ahead",
        "periodicity": "weekly",
        "pattern": "perfect",
    },
    {
        "name": "Clean the House",
        "description": "Thorough house cleaning",
        "periodicity": "weekly",
        "pattern": "struggling",
    },
]

MONTHLY_HABITS = [
    {
        "name": "Financial Check",
        "description": "Review budget and finances",
        "periodicity": "monthly",
        "pattern": "in_progress",
    },
    {
        "name": "Skill Development",
        "description": "Complete a course or learn a new skill",
        "periodicity": "monthly",
        "pattern": "struggling",
    },
]

ALL_HABITS = DAILY_HABITS + WEEKLY_HABITS + MONTHLY_HABITS


def create_users(db: Storage) -> list:
    """Create test users - only guest for testing."""
    users = []
    user_data = [
        {"username": "guest", "password": "guest123", "role": "guest"},
    ]
    for data in user_data:
        user = User(
            username=data["username"],
            email=f"{data['username']}@example.com",
            password=data["password"],
            role=data["role"],
        )
        db.save_user(user)
        users.append(user)
        print(f"  ✅ Created: {user.username} / {data['password']} (role: {user.role})")
    return users


def create_habits_for_user(db: Storage, user: User) -> list:
    """Create 7 habits for a user."""
    habits = []
    for template in ALL_HABITS:
        habit = Habit(
            name=template["name"],
            user_id=user.user_id,
            description=template["description"],
            periodicity=template["periodicity"],
        )
        db.save_habit(habit)
        habits.append(habit)
        print(f"    ✅ Created: {habit.name} ({habit.periodicity})")
    return habits


def add_4_weeks_completions(storage, habit, pattern="perfect"):
    """
    Add 4 weeks (28 days) of completions to a habit based on a pattern.
    """
    if not habit or not habit.habit_id:
        raise ValueError("Habit must be saved before adding completions")

    today = datetime.now()
    start_date = today - timedelta(days=27)

    patterns = {
        "perfect": set(range(28)),
        "struggling": {0, 1, 2, 5, 6, 7, 10, 11, 15, 16, 20},
        "in_progress": {
            0,
            1,
            2,
            3,
            4,
            7,
            8,
            9,
            10,
            13,
            14,
            15,
            16,
            19,
            20,
            21,
            22,
            25,
            26,
            27,
        },
        "average": set(range(0, 28, 2)),
    }

    completion_days = patterns.get(pattern, patterns["average"])
    completions_added = 0

    for day in range(28):
        if day in completion_days:
            completion_date = start_date + timedelta(days=day)
            habit.add_completion(completion_date)
            completions_added += 1

    storage.save_habit(habit)
    return completions_added


def seed_database():
    """Main function to seed the database."""
    print("\n" + "=" * 60)
    print("🌱 SEED DATA GENERATOR")
    print("=" * 60)

    # ✅ get_db_path is now defined above
    db_path = get_db_path()
    print(f"\n📂 Database: {db_path}")

    if os.path.exists(db_path):
        choice = input("  Reset and create fresh data? (y/n): ").strip().lower()
        if choice != "y":
            print("❌ Operation cancelled")
            return
        os.remove(db_path)
        print("  ✅ Database removed")

    db = Storage(db_path)

    try:
        print("\n👤 Creating guest user...")
        users = create_users(db)

        print("\n📋 Creating 7 habits for guest...")
        for user in users:
            print(f"\n  User: {user.username}")
            habits = create_habits_for_user(db, user)

            print("\n📊 Adding 4 weeks of completions...")
            for habit in habits:
                pattern = "average"
                for template in ALL_HABITS:
                    if template["name"] == habit.name:
                        pattern = template.get("pattern", "average")
                        break
                count = add_4_weeks_completions(db, habit, pattern)
                print(f"    ✅ {habit.name}: {count}/28 days")

        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)

        print("\n🔑 Test Account:")
        print("  guest / guest123  (Guest account with 7 habits and 4 weeks data)")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


class PredefinedHabits:
    """Predefined habits for guest account with 4 weeks test data."""

    @classmethod
    def create(cls, user_id: str) -> list:
        """Create 7 habits with 4 weeks of test data for guest account."""
        habits = []
        random.seed(42)
        now = datetime.now()
        start_date = (now - timedelta(days=27)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        for template in ALL_HABITS:
            habit = Habit(
                name=template["name"],
                user_id=user_id,
                description=template["description"],
                periodicity=template["periodicity"],
            )
            habit.habit_id = str(uuid.uuid4())

            pattern = template["pattern"]
            if pattern == "perfect":
                completion_days = list(range(28))
            elif pattern == "struggling":
                completion_days = [0, 1, 2, 5, 6, 10, 14, 15, 16, 20, 25]
            elif pattern == "in_progress":
                completion_days = [
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
                ]
            else:
                completion_days = [i for i in range(28) if random.random() < 0.7]

            for day in completion_days:
                completion_date = start_date + timedelta(days=day)
                completion_date = completion_date.replace(
                    hour=random.randint(6, 22),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                )
                habit.complete(completion_date)
            habits.append(habit)

        return habits


if __name__ == "__main__":
    seed_database()
