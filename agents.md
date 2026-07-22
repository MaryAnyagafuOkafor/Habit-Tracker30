# AGENTS.md - Habit Tracker Project

This file defines the project context, architecture, and coding standards for AI agents and developers working on the Habit Tracker application.

---

## 📋 Project Overview

**Project Name:** Habit Tracker CLI  
**Description:** A command-line habit tracking application with streak analytics, user authentication, role-based access (User/Guest/Admin), and GitHub-style heatmap visualizations.  
**Version:** 0.1.0  
**Status:** In Development (MVP Complete, Reorganization in Progress)

---

## 🛠️ Tech Stack

| Category | Technology | Version |
| :--- | :--- | :--- |
| **Language** | Python | 3.10+ |
| **Database** | SQLite | Built-in |
| **CLI Framework** | Click | 8.2.1 |
| **Interactive Prompts** | Questionary | 2.0.1 |
| **Password Hashing** | Argon2-cffi | 23.1.0 |
| **Testing Framework** | Pytest | 9.1.1 |
| **Test Coverage** | Pytest-cov | 7.1.0 |
| **Code Quality** | Flake8, Pylint, Black | Latest |

### Primary Dependencies (requirements.txt)

---

## 📁 Folder Structure
habit-tracker/
│
├── pyproject.toml # Package config
├── README.md # Project documentation
├── .gitignore # Git ignore file
├── .env.example # Environment variables template
├── pytest.ini # Pytest configuration
│
├── main.py # Application entry point
│
├── src/
│ ├── init.py
│ │
│ ├── core/ # Core business logic
│ │ ├── init.py
│ │ ├── models/ # Domain models
│ │ │ ├── init.py
│ │ │ ├── habit.py
│ │ │ └── user.py
│ │ │
│ │ ├── analytics/ # Analytics logic
│ │ │ ├── init.py
│ │ │ ├── streak.py
│ │ │ └── heatmap.py
│ │ │
│ │ ├── database/ # Data layer
│ │ │ ├── init.py
│ │ │ ├── repository.py
│ │ │ └── migrations/
│ │ │ └── schema.sql
│ │ │
│ │ └── services/ # Service layer
│ │ ├── init.py
│ │ └── habit_service.py
│ │
│ ├── cli/ # CLI presentation layer
│ │ ├── init.py
│ │ └── user_interface.py # ALL CLI commands (ONE FILE)
│ │
│ └── utils/ # Shared utilities
│ ├── init.py
│ └── helpers.py # ALL utilities (ONE FILE)
│
├── tests/ # Unit tests
│ ├── init.py
│ ├── conftest.py
│ ├── core/
│ │ ├── test_habit.py
│ │ ├── test_user.py
│ │ └── test_analytics.py
│ └── database/
│ └── test_repository.py
│
├── data/ # Data directory
│ └── habits.db # SQLite database (gitignored)
│
└── scripts/ # Helper scripts
├── seed_data.py
└── reset_db.py

---

## 🔧 Functions Already Built

### 1. Database Layer (`src/core/database/repository.py`)

| Function | Description | Returns |
| :--- | :--- | :--- |
| `Storage.__init__(db_path)` | Initialize database connection | None |
| `_get_connection()` | Get persistent DB connection | `sqlite3.Connection` |
| `_init_database()` | Create tables and indexes | None |
| `_execute_query()` | Execute SQL query | `Union[int, tuple, list, None]` |
| `user_exists(user_id)` | Check if user exists | `bool` |
| `username_exists(username)` | Check if username exists | `bool` |
| `save_user(user)` | Save or update user | None |
| `get_user_by_username(username)` | Get user by username | `Optional[User]` |
| `get_user_by_id(user_id)` | Get user by ID | `Optional[User]` |
| `get_all_users()` | Get all users | `List[User]` |
| `save_habit(habit)` | Save or update habit | `bool` |
| `get_habit_by_id(habit_id)` | Get habit by ID | `Optional[Habit]` |
| `get_habits_for_user(user_id)` | Get user's habits | `List[Habit]` |
| `get_all_habits()` | Get all habits (admin) | `List[Habit]` |
| `delete_habit(habit_id)` | Soft delete habit | `bool` |
| `add_completion()` | Add completion | `bool` |
| `get_habit_completions()` | Get completions | `List[datetime]` |
| `get_streak_for_habit()` | Get streak info | `Dict[str, Any]` |
| `get_all_habits_with_streaks()` | Get habits with streaks | `List[Dict[str, Any]]` |
| `get_habit_streak_summary()` | Get streak summary | `Dict[str, Any]` |
| `close()` | Close database connection | None |

### 2. Domain Models (`src/core/models/`)

#### `habit.py`

| Function | Description |
| :--- | :--- |
| `Habit.__init__()` | Initialize habit |
| `Habit.complete()` | Add completion |
| `Habit.add_completion()` | Alias for complete() |
| `Habit.add_completions()` | Add multiple completions |
| `Habit.get_period_days()` | Get days per period |
| `Habit.get_period_start()` | Get period start date |
| `Habit.was_completed_in_period()` | Check if completed |
| `Habit.is_broken()` | Check if habit broken |
| `Habit.get_current_streak()` | Get current streak |
| `Habit.get_longest_streak()` | Get longest streak |
| `Habit.get_streak_info()` | Get comprehensive info |
| `Habit.to_dict()` | Serialize to dict |
| `Habit.from_dict()` | Deserialize from dict |

#### `user.py`

| Function | Description |
| :--- | :--- |
| `User.__init__()` | Initialize user |
| `User._hash_password()` | Hash password |
| `User.verify_password()` | Verify password |
| `User.set_password()` | Set new password |
| `User.to_dict()` | Serialize to dict |
| `User.from_dict()` | Deserialize from dict |
| `User.deactivate()` | Deactivate account |
| `User.activate()` | Activate account |
| `User.is_admin()` | Check if admin |
| `User.is_guest()` | Check if guest |
| `User.is_user()` | Check if regular user |

### 3. Analytics (`src/core/analytics/`)

#### `streak.py`

| Function | Description |
| :--- | :--- |
| `calculate_current_streak()` | Calculate current streak |
| `calculate_longest_streak()` | Calculate longest streak |
| `get_habits_by_periodicity()` | Filter habits |
| `get_overall_longest_streak()` | Best streak across habits |
| `get_streak_info()` | Comprehensive streak info |
| `get_habit_with_longest_streak()` | Habit with best streak |
| `create_progress_bar()` | Visual progress bar |
| `display_streak_info()` | Print streak info |
| `display_overall_longest_streak()` | Print best streak |
| `display_full_dashboard()` | Print complete dashboard |

#### `heatmap.py`

| Function | Description |
| :--- | :--- |
| `HabitHeatmap.__init__()` | Initialize heatmap |
| `HabitHeatmap.show()` | Display heatmap |
| `HabitHeatmap.get_completion_count()` | Total completions |
| `HabitHeatmap.get_current_streak()` | Current streak |
| `HabitHeatmap.get_week_stats()` | Weekly statistics |

### 4. Service Layer (`src/core/services/habit_service.py`)

| Function | Description |
| :--- | :--- |
| `HabitManager.__init__()` | Initialize manager |
| `HabitManager.register_user()` | Register new user |
| `HabitManager.login_user()` | Authenticate user |
| `HabitManager.get_username_by_id()` | Get username |
| `HabitManager.create_habit()` | Create new habit |
| `HabitManager.get_habit_by_id()` | Get habit by ID |
| `HabitManager.get_habits_for_user()` | Get user habits |
| `HabitManager.get_user_habits()` | Alias for above |
| `HabitManager.get_all_habits()` | Get all habits (admin) |
| `HabitManager.save_habit_direct()` | Direct save |
| `HabitManager.delete_habit()` | Soft delete |
| `HabitManager.complete_habit()` | Complete habit |
| `HabitManager.get_habit_with_streak()` | Habit with streak |
| `HabitManager.get_all_habits_with_streaks()` | All habits with streaks |
| `HabitManager.get_habit_streak_summary()` | Streak summary |

### 5. CLI Interface (`src/cli/user_interface.py`)

**ALL CLI COMMANDS IN ONE FILE**

| Function | Description |
| :--- | :--- |
| `UserInterface.__init__()` | Initialize UI |
| `UserInterface.run()` | Main app loop |
| `_show_auth_menu()` | Authentication menu |
| `_show_main_menu()` | Role-based menu |
| `_show_user_menu()` | User menu |
| `_show_guest_menu()` | Guest menu |
| `_show_admin_menu()` | Admin menu |
| `_login()` | Login user |
| `_register()` | Register user |
| `_guest_login()` | Guest login |
| `_admin_login()` | Admin login |
| `_logout()` | Logout |
| `_create_first_admin()` | Create first admin |
| `_create_admin_account()` | Create new admin |
| `_view_user_habits()` | View user habits |
| `_create_habit()` | Create habit |
| `_complete_habit()` | Complete habit |
| `_delete_habit()` | Delete habit |
| `_view_heatmap()` | View heatmap |
| `_show_user_dashboard()` | User dashboard |
| `_view_guest_habits()` | View guest habits |
| `_show_guest_dashboard()` | Guest dashboard |
| `_view_all_users()` | View all users (admin) |
| `_view_all_habits_admin()` | View all habits (admin) |
| `_show_admin_dashboard()` | Admin dashboard |


## 📋 Predefined Habit Templates

The application includes **7 predefined habit templates** that are stored in `src/utils/helpers.py`. These are **NOT stored in the database** - they are templates that users can choose from when creating new habits.

### Template Structure

```python
PREDEFINED_HABITS = [
    # Daily habits (3)
    {"name": "Morning Exercise", "periodicity": "daily", "category": "health"},
    {"name": "Read Daily", "periodicity": "daily", "category": "learning"},
    {"name": "Meditate", "periodicity": "daily", "category": "wellness"},
    
    # Weekly habits (2)
    {"name": "Clean the House", "periodicity": "weekly", "category": "chores"},
    {"name": "Weekly Review", "periodicity": "weekly", "category": "productivity"},
    
    # Monthly habits (2)
    {"name": "Financial Check", "periodicity": "monthly", "category": "finance"},
    {"name": "Skill Development", "periodicity": "monthly", "category": "learning"}
]

## 👤 Guest Account

The guest account is a **regular user account** created by the `seed_data.py` script for **testing and demonstration purposes**. It is NOT a special account type with hardcoded habits.

### Guest Account Details

| Property | Value |
| :--- | :--- |
| **Username** | `guest` |
| **Password** | `guest123` |
| **Role** | `user` (not a special role) |
| **Habits** | Created by seed_data.py (3-4 habits with history) |
| **Purpose** | Testing and development only |

### Why Guest is a Regular User

The guest account is **not a special role** in the system. It's simply a pre-created user account that:
1. **Exists in the database** (not hardcoded)
2. **Has habits with historical data** from seed_data.py
3. **Allows developers to quickly test** the application
4. **Demonstrates features** like streaks and heatmaps

### Guest vs. Predefined Habits

| Aspect | Guest Account | Predefined Habits |
| :--- | :--- | :--- |
| **What it is** | A database user with habits | Code templates for suggestions |
| **Stored in** | SQLite database | `src/utils/predefined_habits.py` |
| **Created by** | `seed_data.py` script | Developer (hardcoded) |
| **Has history?** | Yes (completions, streaks) | No (just templates) |
| **Used for** | Testing and demonstration | User suggestions when creating habits |
| **Role** | Regular user (not special) | Not applicable |

---

## 📋 Predefined Habit Templates

The application includes **7 predefined habit templates** stored in `src/utils/predefined_habits.py`. These are **NOT stored in the database** and are **NOT associated with the guest account**.

### Template Structure

```python
# src/utils/predefined_habits.py

from typing import List, Dict, Optional

PREDEFINED_HABITS: List[Dict[str, str]] = [
    # Daily habits (3)
    {
        "name": "Morning Exercise",
        "description": "30 minutes of physical activity",
        "periodicity": "daily",
        "category": "health"
    },
    {
        "name": "Read Daily",
        "description": "Read 20 pages of a book",
        "periodicity": "daily",
        "category": "learning"
    },
    {
        "name": "Meditate",
        "description": "10 minutes of mindfulness meditation",
        "periodicity": "daily",
        "category": "wellness"
    },
    
    # Weekly habits (2)
    {
        "name": "Clean the House",
        "description": "Thorough house cleaning",
        "periodicity": "weekly",
        "category": "chores"
    },
    {
        "name": "Weekly Review",
        "description": "Plan and review the week ahead",
        "periodicity": "weekly",
        "category": "productivity"
    },
    
    # Monthly habits (2)
    {
        "name": "Financial Check",
        "description": "Review budget and finances",
        "periodicity": "monthly",
        "category": "finance"
    },
    {
        "name": "Skill Development",
        "description": "Complete a course or learn a new skill",
        "periodicity": "monthly",
        "category": "learning"
    }
]

def get_predefined_habits() -> List[Dict[str, str]]:
    """Return all predefined habit templates."""
    return PREDEFINED_HABITS.copy()

def get_habits_by_periodicity(periodicity: str) -> List[Dict[str, str]]:
    """Filter templates by periodicity."""
    valid = {'daily', 'weekly', 'monthly'}
    if periodicity not in valid:
        raise ValueError(f"Invalid periodicity: {periodicity}")
    return [h for h in PREDEFINED_HABITS if h['periodicity'] == periodicity]
    
### 6. Utilities (`src/utils/helpers.py`)

**ALL UTILITY FUNCTIONS IN ONE FILE**

| Function | Description |
| :--- | :--- |
| `to_iso()` | Convert datetime to ISO string |
| `from_iso()` | Convert ISO string to datetime |
| `parse_datetime()` | Parse various datetime formats |

---

## ❌ Functions Missing / Not Yet Implemented

| Category | Missing Feature | Priority |
| :--- | :--- | :--- |
| **CLI** | Click Commands | High |
| **Testing** | Unit Tests | High |
| **Testing** | Integration Tests | High |
| **Testing** | Test Coverage >80% | High |
| **Database** | Migrations | Medium |
| **Database** | Export/Import | Medium |
| **Security** | Session Management | Medium |
| **Security** | Environment Variables | Medium |
| **Logging** | Logging System | Medium |
| **Config** | Configuration File | Low |
| **CLI** | Autocomplete | Low |
| **Analytics** | Weekly/Monthly Reports | Low |
| **Documentation** | User Guide | High |

---

## 📏 Coding Standards

### General Principles
- **Readability over cleverness**
- **DRY** - Don't Repeat Yourself
- **Single Responsibility** - Each function does one thing
- **Type Hints** - Use type hints for all function signatures
- **Docstrings** - Every public function must have a docstring
- **Test Coverage** - Aim for >80% coverage with pytest

### Naming Conventions

| Element | Convention | Example |
| :--- | :--- | :--- |
| **Modules** | snake_case | `habit_service.py` |
| **Classes** | PascalCase | `UserInterface`, `HabitManager` |
| **Functions** | snake_case | `create_habit`, `get_all_habits` |
| **Private Methods** | _leading_underscore | `_get_connection` |
| **Variables** | snake_case | `user_id`, `habit_name` |
| **Constants** | UPPER_SNAKE_CASE | `DB_PATH` |
| **Boolean Methods** | is_/has_ prefix | `is_active`, `has_completion` |

### Docstring Format (Google Style)

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Example:
        >>> function_name("test", 5)
        True
    """
    pass
    
# 1. Standard library imports
import os
from datetime import datetime
from typing import List, Optional

# 2. Third-party imports
import click
import questionary

# 3. Local application imports
from src.core.models.habit import Habit
from src.utils.helpers import to_iso

Code Style
Line length: 88 characters (Black default)

Indentation: 4 spaces (no tabs)

Black: Run black . to auto-format

Flake8: Run flake8 src/ tests/ to check style

🧪 Testing Standards
Test Naming
Test files: test_<module_name>.py

Test classes: Test<ClassName>

Test methods: test_<function_name>_<scenario>
def test_habit_creation():
    # Arrange - Set up test data
    habit = Habit("Exercise", "user_1")
    
    # Act - Execute the code being tested
    result = habit.get_current_streak()
    
    # Assert - Verify the result
    assert result == 0
Required Coverage
Minimum coverage: 80%

Critical path: 100% (authentication, streak calculation)

🚀 Development Commands
Command	Description
python main.py	Run the app
pytest	Run all tests
pytest -v	Run tests with verbose output
pytest --cov=src	Run tests with coverage
black .	Auto-format all code
flake8 src/ tests/	Check style issues
📝 Key File Import Map
File	Imports From
src/core/models/habit.py	src.utils.helpers
src/core/models/user.py	src.utils.helpers, argon2
src/core/analytics/streak.py	src.core.models.habit
src/core/analytics/heatmap.py	src.core.models.habit
src/core/database/repository.py	src.core.models.habit, src.core.models.user, src.utils.helpers
src/core/services/habit_service.py	src.core.database.repository, src.core.models.habit, src.core.models.user, src.core.analytics.streak
src/cli/user_interface.py	src.core.database.repository, src.core.services.habit_service, src.core.models.user, src.core.models.habit, src.core.analytics.streak, src.core.analytics.heatmap, src.utils.helpers
scripts/seed_data.py	src.core.models.habit
main.py	src.cli.user_interface
🎯 Next Steps (Prioritized)
Priority	Task
1	Fix habit_service.py import bug
2	Run python main.py and verify app works
3	Reorganize folder structure (file-by-file)
4	Write unit tests for habit.py
5	Write unit tests for streak.py
6	Write unit tests for repository.py
7	Add Click CLI commands
8	Add proper logging system
📚 Resources
Click Documentation

Questionary Documentation

Pytest Documentation

Argon2 Documentation

SQLite Documentation

