"""
SHARED TEST FIXTURES - Pytest Configuration
============================================

This module provides shared pytest fixtures for all tests.

Key Features:
    - Temporary database fixtures
    - Test user and habit fixtures
    - Sample data for analytics tests
    - Mock fixtures for CLI testing
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Also add scripts path
scripts_path = os.path.join(project_root, "scripts")
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)


import pytest
import tempfile
from datetime import datetime, timedelta

from src.core.database.repository import Storage
from src.core.models.habit import Habit
from src.core.models.user import User
from src.core.services.habit_service import HabitManager

# ============================================================
# DATABASE FIXTURES
# ============================================================


@pytest.fixture
def temp_db():
    """
    Create a temporary database for testing.

    This fixture creates a temporary SQLite database file
    that is automatically deleted after the test completes.
    """
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    storage = Storage(temp_path)
    yield storage

    storage.close()
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def storage(temp_db):
    """Alias for temp_db fixture."""
    return temp_db


@pytest.fixture
def manager(temp_db):
    """Create a HabitManager instance."""
    return HabitManager(temp_db)


@pytest.fixture
def habit_service(storage):
    """Create a HabitService instance with test database."""
    return HabitManager(storage)


# ============================================================
# TEST DATA FIXTURES
# ============================================================

@pytest.fixture
def test_user(temp_db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@email.com",
        password="password",
        role="user"
    )
    temp_db.save_user(user)  # ✅ Make sure this is called!
    return user


@pytest.fixture
def test_admin():
    """Create a test admin user."""
    return User(
        username="admin", email="admin@example.com", password="admin123", role="admin"
    )


@pytest.fixture
def test_guest():
    """Create a test guest user."""
    return User(
        username="guest", email="", password="guest123", user_id="guest", role="guest"
    )


@pytest.fixture
def test_habit(test_user):
    """Create a test habit."""
    return Habit(
        name="Exercise",
        user_id=test_user.user_id,
        description="Daily exercise routine",
        periodicity="daily",
    )


@pytest.fixture
def test_habit_weekly(test_user):
    """Create a weekly test habit."""
    return Habit(
        name="Weekly Review",
        user_id=test_user.user_id,
        description="Review weekly progress",
        periodicity="weekly",
    )


@pytest.fixture
def test_habit_monthly(test_user):
    """Create a monthly test habit."""
    return Habit(
        name="Monthly Goal",
        user_id=test_user.user_id,
        description="Set monthly goals",
        periodicity="monthly",
    )


@pytest.fixture
def test_habit_with_completions(test_user):
    """Create a habit with 5 days of completions."""
    habit = Habit(
        name="Exercise",
        user_id=test_user.user_id,
        description="Daily exercise routine",
        periodicity="daily",
    )

    today = datetime.now()
    for i in range(5):
        habit.complete(today - timedelta(days=i))

    return habit


@pytest.fixture
def saved_test_user(storage, test_user):
    """Save a test user to the database."""
    storage.save_user(test_user)
    return test_user


@pytest.fixture
def saved_test_habit(storage, saved_test_user, test_habit):
    """Save a test habit to the database."""
    test_habit.user_id = saved_test_user.user_id
    storage.save_habit(test_habit)
    return test_habit


@pytest.fixture
def saved_test_habit_with_completions(
    storage, saved_test_user, test_habit_with_completions
):
    """Save a test habit with completions to the database."""
    test_habit_with_completions.user_id = saved_test_user.user_id
    storage.save_habit(test_habit_with_completions)
    return test_habit_with_completions


@pytest.fixture
def test_update_habit(temp_db, test_user):
    storage = temp_db
    storage.save_user(test_user)

    # ✅ Create a NEW habit with your own name
    habit = Habit(
        name="Test Habit",  # ← This should be saved
        user_id=test_user.user_id,
        description="Test description",
        periodicity="daily",
    )
    storage.save_habit(habit)

    # ✅ Fetch it
    fetched = storage.get_habit_by_id(habit.habit_id)

    # ✅ This should now pass
    # noinspection PyUnresolvedReferences
    assert fetched.name == "Test Habit"


# ============================================================
# SAMPLE HABITS FOR ANALYTICS TESTS
# ============================================================


@pytest.fixture
def sample_habits(test_user):
    """Create a list of sample habits for testing analytics."""
    habits = []

    # Daily habit with 5-day streak
    h1 = Habit("Exercise", test_user.user_id, "Daily exercise", "daily")
    today = datetime.now()
    for i in range(5):
        h1.complete(today - timedelta(days=i))
    habits.append(h1)

    # Weekly habit with 3-week streak
    h2 = Habit("Weekly Review", test_user.user_id, "Weekly review", "weekly")
    for i in range(3):
        h2.complete(today - timedelta(weeks=i))
    habits.append(h2)

    # Monthly habit with 2-month streak
    h3 = Habit("Monthly Goal", test_user.user_id, "Monthly goal", "monthly")
    h3.complete(today - timedelta(days=30))
    h3.complete(today - timedelta(days=60))
    habits.append(h3)

    return habits


# ============================================================
# MOCK FIXTURES
# ============================================================


@pytest.fixture
def mock_questionary(monkeypatch):
    """Mock questionary prompts for testing CLI."""

    def mock_text(prompt):
        if "name" in prompt.lower() or "habit" in prompt.lower():
            return "Exercise"
        if "email" in prompt.lower():
            return "test@example.com"
        if "password" in prompt.lower():
            return "password123"
        if "username" in prompt.lower():
            return "testuser"
        return "test"

    def mock_select(prompt, choices):
        if "periodicity" in prompt.lower() or "period" in prompt.lower():
            return "daily"
        return choices[0] if choices else ""

    def mock_confirm():
        return True

    monkeypatch.setattr("questionary.text", mock_text)
    monkeypatch.setattr("questionary.password", mock_text)
    monkeypatch.setattr("questionary.select", mock_select)
    monkeypatch.setattr("questionary.confirm", mock_confirm)


@pytest.fixture
def mock_cli_inputs(monkeypatch):
    """Mock all CLI inputs for testing."""
    inputs = {
        "username": "testuser",
        "password": "password123",
        "habit_name": "Exercise",
        "periodicity": "daily",
        "description": "Daily exercise",
        "confirm": True,
    }

    def mock_text(prompt):
        if "username" in prompt.lower():
            return inputs["username"]
        if "password" in prompt.lower():
            return inputs["password"]
        if "name" in prompt.lower() or "habit" in prompt.lower():
            return inputs["habit_name"]
        if "email" in prompt.lower():
            return "test@example.com"
        if "description" in prompt.lower():
            return inputs["description"]
        return "test"

    def mock_select(prompt, choices):
        if "periodicity" in prompt.lower():
            return inputs["periodicity"]
        return choices[0] if choices else ""

    def mock_confirm():
        return inputs["confirm"]

    monkeypatch.setattr("questionary.text", mock_text)
    monkeypatch.setattr("questionary.password", mock_text)
    monkeypatch.setattr("questionary.select", mock_select)
    monkeypatch.setattr("questionary.confirm", mock_confirm)

    return inputs
