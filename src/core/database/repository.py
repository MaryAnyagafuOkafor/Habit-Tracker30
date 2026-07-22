"""
DATABASE REPOSITORY - Data Layer
================================

This module handles all database operations for the Habit Tracker application.
It provides an abstraction layer over SQLite, managing:
    - User CRUD operations
    - Habit CRUD operations
    - Completion tracking
    - Streak calculations and queries

Key Features:
    - SQLite database with foreign key constraints
    - Automatic schema creation
    - Indexed queries for performance
    - Transaction support
    - Type conversion between Python and SQLite

Example:
    >>> storage = Storage("habits.db")
    >>> user = User("john", "john@email.com", "password")
    >>> storage.save_user(user)
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.models.habit import Habit
from src.core.models.user import User
from src.utils.helpers import from_iso, get_db_path, to_iso


class Storage:
    """
    Data Layer for Habit Tracker Application.

    This class manages all database operations including:
        - User management (create, read, update)
        - Habit management (create, read, update, delete)
        - Completion tracking
        - Streak calculations

    Attributes:
        db_path (str): Path to SQLite database file

    Example:
        >>> storage = Storage("habits.db")
        >>> user = User("john", "john@email.com", "password")
        >>> storage.save_user(user)
    """

    # ============================================
    # 2.1 INITIALIZATION
    # ============================================

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to database file. If None, uses default path.
        """
        if db_path is None:
            db_path = get_db_path()

        self.db_path = db_path
        self.connection = None
        self._analyzer = None  # Cache StreakAnalyzer instance
        self._init_database()

    def _get_analyzer(self):
        """Get or create the StreakAnalyzer instance."""
        if self._analyzer is None:
            from src.analytics.streak import StreakAnalyzer

            self._analyzer = StreakAnalyzer()
        return self._analyzer

    def _get_connection(self) -> sqlite3.Connection:
        """Get persistent database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def _init_database(self) -> None:
        """Create tables and indexes if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS habits (
                habit_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                periodicity TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS habit_completions (
                completion_id TEXT PRIMARY KEY,
                habit_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (habit_id) REFERENCES habits(habit_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        # Create indexes for performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_habits_is_active ON habits(is_active)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_completions_habit_id ON habit_completions(habit_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_completions_user_id ON habit_completions(user_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_completions_completed_at ON habit_completions(completed_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
        )

        conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    # ============================================
    # DATABASE CONNECTION HELPER
    # ============================================

    def _execute_query(
        self,
        query: str,
        params: tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False,
    ):
        """
        Execute a database query using the persistent connection.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            print(f"   Query: {query[:100]}...")
            return None

    # ============================================
    # USER MANAGEMENT
    # ============================================

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists in the database by ID."""
        result = self._execute_query(
            "SELECT 1 FROM users WHERE user_id = ?", (user_id,), fetch_one=True
        )
        return result is not None

    def username_exists(self, username: str) -> bool:
        """Check if a username exists in the database."""
        result = self._execute_query(
            "SELECT 1 FROM users WHERE username = ?", (username,), fetch_one=True
        )
        return result is not None

    def save_user(self, user: User) -> None:
        """Save a user to the database (insert or update)."""
        data = user.to_dict()
        created_at = to_iso(data.get("created_at"))

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO users 
            (user_id, username, email, password_hash, created_at, is_active, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["user_id"],
                data["username"],
                data.get("email", ""),
                data["password_hash"],
                created_at,
                data.get("is_active", 1),
                data.get("role", "user"),
            ),
        )
        conn.commit()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        row = self._execute_query(
            "SELECT * FROM users WHERE username = ?", (username,), fetch_one=True
        )
        if row:
            return self._row_to_user(row)
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID."""
        row = self._execute_query(
            "SELECT * FROM users WHERE user_id = ?", (user_id,), fetch_one=True
        )
        if row:
            return self._row_to_user(row)
        return None

    def get_all_users(self) -> List[User]:
        """Get all users in the system (admin function)."""
        users = []
        rows = self._execute_query("SELECT * FROM users", (), fetch_all=True)
        if rows:
            for row in rows:
                users.append(self._row_to_user(row))
        return users

    # ============================================
    # HABIT MANAGEMENT
    # ============================================

    def save_habit(self, habit: Habit) -> bool:
        """
        Save a habit to the database (insert or update).

        Returns:
            bool: True if save was successful, False otherwise
        """
        data = habit.to_dict()

        # Check if user exists before saving
        if not self.user_exists(data["user_id"]):
            print(f"❌ ERROR: User {data['user_id']} does not exist!")
            print(f"   Cannot save habit '{data['name']}'")
            return False

        if isinstance(data["created_at"], datetime):
            created_at = to_iso(data["created_at"])
        else:
            created_at = data["created_at"]

        conn = self._get_connection()
        cursor = conn.cursor()

        # Save the habit
        cursor.execute(
            """
            INSERT OR REPLACE INTO habits 
            (habit_id, user_id, name, description, periodicity, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["habit_id"],
                data["user_id"],
                data["name"],
                data.get("description", ""),
                data["periodicity"],
                created_at,
                1 if habit.is_active else 0,
            ),
        )

        # Delete old completions
        cursor.execute(
            "DELETE FROM habit_completions WHERE habit_id = ?", (data["habit_id"],)
        )

        # Save completions
        for completion_date in data.get("completions", []):
            if isinstance(completion_date, datetime):
                timestamp = to_iso(completion_date)
            else:
                timestamp = completion_date

            completion_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO habit_completions
                (completion_id, habit_id, user_id, completed_at, count, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (completion_id, data["habit_id"], data["user_id"], timestamp, 1, None),
            )

        conn.commit()
        return True

    def save_habit_direct(self, habit: Habit) -> bool:
        """
        Save a habit directly without checking for existing completions.
        Used for bulk loading and test data.

        Returns:
            bool: True if save was successful, False otherwise
        """
        return self.save_habit(habit)

    def get_habit_by_id(self, habit_id: str) -> Optional[Habit]:
        """Get a habit by its ID with all completions."""
        row = self._execute_query(
            "SELECT * FROM habits WHERE habit_id = ?", (habit_id,), fetch_one=True
        )
        if row:
            habit = self._row_to_habit(row)
            if habit:
                completions = self._get_habit_completions(habit_id)
                habit.completions = completions
            return habit
        return None

    def get_habits_for_user(self, user_id: str) -> List[Habit]:
        """Get all active habits for a user."""
        habits = []
        rows = self._execute_query(
            "SELECT * FROM habits WHERE user_id = ? AND is_active = 1",
            (user_id,),
            fetch_all=True,
        )
        if rows:
            for row in rows:
                habit = self._row_to_habit(row)
                if habit:
                    completions = self._get_habit_completions(habit.habit_id)
                    habit.completions = completions
                    habits.append(habit)
        return habits

    def get_all_habits(self) -> List[Habit]:
        """Get all active habits from all users (admin function)."""
        habits = []
        rows = self._execute_query(
            "SELECT * FROM habits WHERE is_active = 1", (), fetch_all=True
        )
        if rows:
            for row in rows:
                habit = self._row_to_habit(row)
                if habit:
                    completions = self._get_habit_completions(habit.habit_id)
                    habit.completions = completions
                    habits.append(habit)
        return habits

    def delete_habit(self, habit_id: str) -> bool:
        """
        Soft delete a habit and remove its completions.

        Args:
            habit_id: ID of the habit to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if not habit_id:
            return False

        try:
            # Check if habit exists and is active
            habit = self.get_habit_by_id(habit_id)
            if not habit:
                return False

            # ✅ Delete completions first
            self._execute_query(
                "DELETE FROM habit_completions WHERE habit_id = ?",
                (habit_id,)
            )

            # ✅ Soft delete the habit
            query = "UPDATE habits SET is_active = 0 WHERE habit_id = ? AND is_active = 1"
            result = self._execute_query(query, (habit_id,))

            # ✅ Check if any row was actually updated
            if result is not None and result > 0:
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting habit: {e}")
            return False

    def hard_delete_habit(self, habit_id: str) -> bool:
        """
        Permanently delete a habit and its completions.
        """
        if not habit_id:
            return False

        try:
            # Delete completions
            self._execute_query(
                "DELETE FROM habit_completions WHERE habit_id = ?",
                (habit_id,)
            )

            # Delete habit
            query = "DELETE FROM habits WHERE habit_id = ?"
            result = self._execute_query(query, (habit_id,))
            return result is not None
        except Exception as e:
            print(f"❌ Error permanently deleting habit: {e}")
            return False

    def restore_habit(self, habit_id: str) -> bool:
        """
        Restore a soft-deleted habit.
        """
        if not habit_id:
            return False

        try:
            query = "UPDATE habits SET is_active = 1 WHERE habit_id = ? AND is_active = 0"
            result = self._execute_query(query, (habit_id,))
            return result is not None
        except Exception as e:
            print(f"❌ Error restoring habit: {e}")
            return False

    # ============================================
    # COMPLETION MANAGEMENT
    # ============================================

    def add_completion(
        self,
        habit_id: str,
        completed_at: Optional[datetime] = None,
        count: int = 1,
        notes: str = None,
    ) -> bool:
        """Add a completion record for a habit."""
        if completed_at is None:
            completed_at = datetime.now()

        # Get the user_id for this habit
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            print(f"❌ Habit {habit_id} not found")
            return False

        user_id = habit.user_id
        timestamp = to_iso(completed_at)
        completion_id = str(uuid.uuid4())

        # Check if completion already exists for this date
        existing = self._execute_query(
            "SELECT 1 FROM habit_completions WHERE habit_id = ? AND completed_at = ?",
            (habit_id, timestamp),
            fetch_one=True,
        )

        if existing:
            # Update count if exists
            result = self._execute_query(
                """
                UPDATE habit_completions 
                SET count = count + ?, notes = ? 
                WHERE habit_id = ? AND completed_at = ?
                """,
                (count, notes, habit_id, timestamp),
            )
            return result is not None and result > 0

        # Insert new completion
        result = self._execute_query(
            """
            INSERT INTO habit_completions
            (completion_id, habit_id, user_id, completed_at, count, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (completion_id, habit_id, user_id, timestamp, count, notes),
        )
        return result is not None and result > 0

    def get_habit_completions(
        self,
        habit_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[datetime]:
        """Get completions for a habit within a date range."""
        return self._get_habit_completions(habit_id, start_date, end_date)

    def _get_habit_completions(
        self,
        habit_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[datetime]:
        """
        Internal method to get completions for a habit.
        """
        completions = []

        query = "SELECT completed_at FROM habit_completions WHERE habit_id = ?"
        params = [habit_id]

        if start_date:
            query += " AND completed_at >= ?"
            params.append(to_iso(start_date))
        if end_date:
            query += " AND completed_at <= ?"
            params.append(to_iso(end_date))

        query += " ORDER BY completed_at"

        rows = self._execute_query(query, tuple(params), fetch_all=True)

        if rows:
            for row in rows:
                if row and len(row) > 0:
                    date_value = row[0]
                    if date_value:
                        # Check if it's a UUID (36 chars with hyphens)
                        if (
                            isinstance(date_value, str)
                            and len(date_value) == 36
                            and date_value.count("-") == 4
                        ):
                            continue
                        dt = from_iso(date_value)
                        if dt:
                            completions.append(dt)

        return completions

    # ============================================
    # UPDATE METHODS
    # ============================================

    def update_habit(self, habit: Habit) -> bool:
        """
        Update an existing habit in the database.

        Args:
            habit: Habit object with updated fields

        Returns:
            bool: True if update was successful, False otherwise
        """
        data = habit.to_dict()

        # Check if habit exists
        if not self.get_habit_by_id(data["habit_id"]):
            print(f"❌ Habit {data['habit_id']} not found")
            return False

        # Check if user exists
        if not self.user_exists(data["user_id"]):
            print(f"❌ User {data['user_id']} does not exist!")
            return False

        conn = self._get_connection()
        cursor = conn.cursor()

        # Update the habit
        cursor.execute(
            """
            UPDATE habits
            SET name = ?,
                description = ?,
                periodicity = ?,
                is_active = ?
            WHERE habit_id = ?
            """,
            (
                data["name"],
                data.get("description", ""),
                data["periodicity"],
                1 if habit.is_active else 0,
                data["habit_id"],
            ),
        )

        conn.commit()

        # Check if any rows were updated
        return cursor.rowcount > 0

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

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE habits SET name = ? WHERE habit_id = ?",
            (new_name.strip(), habit_id),
        )

        conn.commit()
        return cursor.rowcount > 0

    def update_habit_description(self, habit_id: str, new_description: str) -> bool:
        """
        Update a habit's description.

        Args:
            habit_id: ID of the habit to update
            new_description: New description for the habit

        Returns:
            bool: True if update was successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE habits SET description = ? WHERE habit_id = ?",
            (new_description, habit_id),
        )

        conn.commit()
        return cursor.rowcount > 0

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

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE habits SET periodicity = ? WHERE habit_id = ?",
            (new_periodicity, habit_id),
        )

        conn.commit()
        return cursor.rowcount > 0

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
        habit = self.get_habit_by_id(habit_id)
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
        return self.update_habit(habit)

    # ============================================
    # STREAK QUERY METHODS
    # ============================================

    def get_streak_for_habit(self, habit_id: str) -> Dict[str, Any]:
        """Get streak information for a specific habit."""
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return {
                "current": 0,
                "best": 0,
                "target": 0,
                "target_display": "N/A",
                "progress": 0,
                "status": "NOT FOUND",
            }

        return self._get_analyzer().get_streak_info(habit)

    def get_habit_with_streak(self, habit_id: str) -> Dict[str, Any]:
        """
        Get a habit with its streak information.

        Returns:
            dict: Contains habit data and streak_info
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return {"habit": None, "streak_info": None}

        streak_info = self._get_analyzer().get_streak_info(habit)
        return {
            "habit": habit,
            "streak_info": streak_info,
        }

    def get_all_habits_with_streaks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all habits for a user with streak information."""
        habits = self.get_habits_for_user(user_id)
        result = []
        analyzer = self._get_analyzer()

        for habit in habits:
            streak_info = analyzer.get_streak_info(habit)
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

    # ============================================
    # HELPER METHODS (Row Conversion)
    # ============================================

    @staticmethod
    def _row_to_user(row) -> User:
        """Convert a database row to a User object."""
        try:
            user_data = {
                "user_id": row["user_id"],
                "username": row["username"],
                "email": row["email"] if "email" in row.keys() else "",
                "password_hash": row["password_hash"],
                "created_at": row["created_at"],
                "is_active": (
                    bool(row["is_active"]) if "is_active" in row.keys() else True
                ),
                "role": row["role"] if "role" in row.keys() else "user",
            }
            return User.from_dict(user_data)
        except Exception as e:
            print(f"❌ Error converting row to user: {e}")
            raise

    @staticmethod
    def _row_to_habit(row) -> Optional[Habit]:
        """Convert a database row to a Habit object."""
        try:
            habit = Habit(
                name=row["name"], user_id=row["user_id"], periodicity=row["periodicity"]
            )
            habit.habit_id = row["habit_id"]
            habit.description = (
                row["description"] if "description" in row.keys() else ""
            )
            habit.is_active = (
                bool(row["is_active"]) if "is_active" in row.keys() else True
            )
            habit.created_at = (
                from_iso(row["created_at"]) if row["created_at"] else datetime.now()
            )
            habit.completions = []
            return habit

        except Exception as e:
            print(f"❌ Error converting row to habit: {e}")
            return None
