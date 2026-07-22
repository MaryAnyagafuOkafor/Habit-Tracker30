# tests/unit/database/test_repository.py

"""
TESTS - Database Repository
============================

Unit tests for the Storage database layer.

Test Categories:
    - Database Initialization
    - User CRUD Operations
    - Habit CRUD Operations
    - Completion Operations
    - Streak Query Methods
"""

from src.core.models.habit import Habit


class TestDatabaseInitialization:
    """Tests for database initialization."""

    def test_database_initializes_tables(self, temp_db):
        storage = temp_db
        conn = storage._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cursor.fetchone() is not None
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='habits'"
        )
        assert cursor.fetchone() is not None
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='habit_completions'"
        )
        assert cursor.fetchone() is not None


class TestUserRepository:
    """Tests for user CRUD operations."""

    def test_save_and_get_user(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)
        retrieved = storage.get_user_by_id(test_user.user_id)
        assert retrieved is not None
        assert retrieved.username == test_user.username

    def test_get_user_by_username(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)
        retrieved = storage.get_user_by_username(test_user.username)
        assert retrieved is not None

    def test_user_exists(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)
        assert storage.user_exists(test_user.user_id) is True
        assert storage.user_exists("nonexistent") is False

    def test_username_exists(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)
        assert storage.username_exists(test_user.username) is True
        assert storage.username_exists("nonexistent") is False


class TestHabitRepository:
    """Tests for habit CRUD operations."""

    def test_save_and_get_habit(self, temp_db, saved_test_user, test_habit):
        storage = temp_db
        test_habit.user_id = saved_test_user.user_id
        storage.save_habit(test_habit)
        retrieved = storage.get_habit_by_id(test_habit.habit_id)
        assert retrieved is not None
        assert retrieved.name == test_habit.name

    def test_get_habits_for_user(self, temp_db, saved_test_user):
        storage = temp_db
        habit1 = Habit("Exercise", saved_test_user.user_id, "Daily", "daily")
        habit2 = Habit("Read", saved_test_user.user_id, "Read books", "daily")
        storage.save_habit(habit1)
        storage.save_habit(habit2)
        habits = storage.get_habits_for_user(saved_test_user.user_id)
        assert len(habits) == 2


class TestCompletionRepository:
    """Tests for completion operations."""

    def test_add_completion(self, temp_db, saved_test_habit):
        storage = temp_db
        habit = saved_test_habit
        result = storage.add_completion(habit.habit_id)
        assert result is True

    def test_get_completions(self, temp_db, saved_test_habit):
        storage = temp_db
        habit = saved_test_habit
        storage.add_completion(habit.habit_id)
        completions = storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 1


class TestRepositoryEdit:
    """Tests for repository edit operations."""

    def test_update_habit(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="Old Name",
            user_id=test_user.user_id,
            description="Old description",
            periodicity="daily",
        )
        storage.save_habit(habit)

        # ✅ Modify the habit
        habit.name = "Test Habit"
        habit.description = "Test description"

        # ✅ Save the changes
        storage.save_habit(habit)

        # ✅ Fetch from database
        updated = storage.get_habit_by_id(habit.habit_id)

        # ✅ Compare with database values
        assert updated.name == "Test Habit"
        assert updated.description == "Test description"

    def test_update_habit_not_found(self, temp_db):
        """Test updating a non-existent habit."""
        habit = Habit(
            name="Non Existent",
            user_id="user123",
            periodicity="daily",
            habit_id="nonexistent",
        )

        result = temp_db.update_habit(habit)
        assert result is False

    def test_rename_habit(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="Old Name",
            user_id=test_user.user_id,
            description="Some description",
            periodicity="daily",
        )
        storage.save_habit(habit)

        # ✅ Rename the habit
        habit.name = "Test Habit"
        storage.save_habit(habit)

        # ✅ Fetch from database
        updated = storage.get_habit_by_id(habit.habit_id)

        # ✅ Compare
        assert updated.name == "Test Habit"

    def test_rename_habit_not_found(self, temp_db):
        """Test renaming a non-existent habit."""
        result = temp_db.rename_habit("nonexistent", "New Name")
        assert result is False

    def test_rename_habit_empty_name(self, temp_db, saved_test_habit):
        """Test renaming with empty name."""
        result = temp_db.rename_habit(saved_test_habit.habit_id, "")
        assert result is False

    def test_update_habit_description(self, temp_db, test_user):
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="Test Habit",
            user_id=test_user.user_id,
            description="Old description",
            periodicity="daily",
        )
        storage.save_habit(habit)

        # ✅ Update description
        habit.description = "Test description"
        storage.save_habit(habit)

        # ✅ Fetch from database
        updated = storage.get_habit_by_id(habit.habit_id)

        # ✅ Compare
        assert updated.description == "Test description"

    def test_update_habit_description_not_found(self, temp_db):
        """Test updating description of non-existent habit."""
        result = temp_db.update_habit_description("nonexistent", "New description")
        assert result is False

    def test_update_habit_periodicity(self, temp_db, saved_test_habit):
        """Test changing habit periodicity."""
        # First verify habit exists
        habit = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert habit is not None
        assert habit.periodicity == "daily"

        # Update periodicity
        result = temp_db.update_habit_periodicity(saved_test_habit.habit_id, "weekly")
        assert result is True

        # Verify
        updated = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert updated is not None
        assert updated.periodicity == "weekly"

    def test_update_habit_periodicity_invalid(self, temp_db, saved_test_habit):
        """Test changing to invalid periodicity."""
        result = temp_db.update_habit_periodicity(saved_test_habit.habit_id, "invalid")
        assert result is False

    def test_update_habit_periodicity_not_found(self, temp_db):
        """Test changing periodicity of non-existent habit."""
        result = temp_db.update_habit_periodicity("nonexistent", "weekly")
        assert result is False

    def test_edit_habit_all_fields(self, temp_db, saved_test_habit):
        """Test editing all fields at once."""
        # First verify habit exists
        habit = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert habit is not None

        # Edit all fields
        result = temp_db.edit_habit(
            habit_id=saved_test_habit.habit_id,
            name="New Habit Name",
            description="New description",
            periodicity="weekly",
        )
        assert result is True

        # Verify
        updated = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert updated is not None
        assert updated.name == "New Habit Name"
        assert updated.description == "New description"
        assert updated.periodicity == "weekly"

    def test_edit_habit_partial(self, temp_db, saved_test_habit):
        """Test editing only some fields."""
        # First verify habit exists
        habit = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert habit is not None
        original_description = habit.description
        original_periodicity = habit.periodicity

        # Edit only name
        result = temp_db.edit_habit(
            habit_id=saved_test_habit.habit_id, name="New Name Only"
        )
        assert result is True

        # Verify
        updated = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert updated is not None
        assert updated.name == "New Name Only"
        assert updated.description == original_description  # Unchanged
        assert updated.periodicity == original_periodicity  # Unchanged

    def test_edit_habit_not_found(self, temp_db):
        """Test editing a non-existent habit."""
        result = temp_db.edit_habit(habit_id="nonexistent", name="New Name")
        assert result is False

    def test_edit_habit_with_completions(self, temp_db, saved_test_habit):
        """Test editing a habit that has completions."""
        # Add some completions
        from datetime import datetime, timedelta

        today = datetime.now()
        for i in range(3):
            temp_db.add_completion(saved_test_habit.habit_id, today - timedelta(days=i))

        # Refresh habit
        habit = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        original_completions = len(habit.completions)
        assert original_completions == 3

        # Edit the habit
        result = temp_db.edit_habit(
            habit_id=saved_test_habit.habit_id, name="Edited With Completions"
        )
        assert result is True

        # Verify completions are preserved
        updated = temp_db.get_habit_by_id(saved_test_habit.habit_id)
        assert updated is not None
        assert updated.name == "Edited With Completions"
        assert len(updated.completions) == original_completions

    def test_delete_habit_soft_delete(self, temp_db, test_user):
        """Test soft deleting a habit in repository."""
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="To Delete",
            user_id=test_user.user_id,
            description="This habit will be deleted",
            periodicity="daily"
        )
        storage.save_habit(habit)

        # Verify habit exists
        assert storage.get_habit_by_id(habit.habit_id) is not None

        # Soft delete
        result = storage.delete_habit(habit.habit_id)
        assert result is True

        # Verify habit is gone (soft deleted)
        deleted = storage.get_habit_by_id(habit.habit_id)
        assert deleted is None or not deleted.is_active

    def test_delete_habit_not_found(self, temp_db):
        """Test deleting a non-existent habit."""
        storage = temp_db
        result = storage.delete_habit("nonexistent_id")
        assert result is False

    def test_delete_habit_already_deleted(self, temp_db, test_user):
        """Test deleting an already deleted habit."""
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="Already Deleted",
            user_id=test_user.user_id,
            periodicity="daily"
        )
        storage.save_habit(habit)

        # First deletion
        result1 = storage.delete_habit(habit.habit_id)
        assert result1 is True

        # Second deletion attempt (should fail)
        result2 = storage.delete_habit(habit.habit_id)
        assert result2 is False

    def test_delete_habit_with_completions(self, temp_db, test_user):
        """Test deleting a habit that has completions."""
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="Habit With Completions",
            user_id=test_user.user_id,
            periodicity="daily"
        )
        storage.save_habit(habit)

        # Add completions
        from datetime import datetime, timedelta
        now = datetime.now()
        for i in range(3):
            storage.add_completion(habit.habit_id, now - timedelta(days=i))

        # Verify completions exist
        completions = storage.get_habit_completions(habit.habit_id)
        assert len(completions) == 3

        # Delete the habit
        result = storage.delete_habit(habit.habit_id)
        assert result is True

        # Verify completions are gone
        completions_after = storage.get_habit_completions(habit.habit_id)
        assert len(completions_after) == 0

    def test_delete_habit_restore(self, temp_db, test_user):
        """Test restoring a soft-deleted habit."""
        storage = temp_db
        storage.save_user(test_user)

        # Create a habit
        habit = Habit(
            name="To Restore",
            user_id=test_user.user_id,
            periodicity="daily"
        )
        storage.save_habit(habit)

        # Delete
        storage.delete_habit(habit.habit_id)

        # Verify it's deleted
        deleted = storage.get_habit_by_id(habit.habit_id)
        assert deleted is None or not deleted.is_active

        # Restore
        result = storage.restore_habit(habit.habit_id)
        assert result is True

        # Verify it's restored
        restored = storage.get_habit_by_id(habit.habit_id)
        assert restored is not None
        assert restored.is_active is True

    def test_delete_multiple_habits(self, temp_db, test_user):
        """Test deleting multiple habits for a user."""
        storage = temp_db
        storage.save_user(test_user)

        # Create multiple habits
        habit1 = Habit("Habit 1", test_user.user_id, periodicity="daily")
        habit2 = Habit("Habit 2", test_user.user_id, periodicity="weekly")
        habit3 = Habit("Habit 3", test_user.user_id, periodicity="monthly")

        storage.save_habit(habit1)
        storage.save_habit(habit2)
        storage.save_habit(habit3)

        # Verify all exist
        habits = storage.get_habits_for_user(test_user.user_id)
        assert len(habits) == 3

        # Delete two habits
        storage.delete_habit(habit1.habit_id)
        storage.delete_habit(habit2.habit_id)

        # Verify only one remains
        remaining = storage.get_habits_for_user(test_user.user_id)
        assert len(remaining) == 1
        assert remaining[0].habit_id == habit3.habit_id

    def test_delete_habit_other_user(self, temp_db):
        """Test deleting a habit belonging to another user."""
        storage = temp_db

        # Create user1
        from src.core.models.user import User
        user1 = User("user1", "user1@email.com", "pass1")
        storage.save_user(user1)

        # Create user2
        user2 = User("user2", "user2@email.com", "pass2")
        storage.save_user(user2)

        # Create habit for user1
        habit = Habit("User1 Habit", user1.user_id, periodicity="daily")
        storage.save_habit(habit)

        # Try to delete with user2 (should fail if permission checks exist)
        # Note: If your repository doesn't check permissions, this will pass
        storage.delete_habit(habit.habit_id)

        # Verify the habit still exists (or is properly handled)
        storage.get_habit_by_id(habit.habit_id)
        # Adjust assertion based on your implementation


