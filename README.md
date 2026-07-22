Habit Tracker CLI
A command-line habit tracking application with streak analytics, user authentication, role-based access (User/Guest/Admin), and GitHub-style heatmap visualizations. 
Table of Contents
1.   Overview
2.   Features
3.   Tech Stack
4.   Installation
5.   Project Structure
6.   Architecture
7.   user Guide
8.   Database Schema
9.   Testing
10.  Development

1.  Overview
Habit Tracker CLI is a powerful command-line application designed to help users build and maintain positive habits. It combines the simplicity of a CLI with robust features like:
User Authentication – Secure registration and login
Role-Based Access – User, Guest, and Admin roles with appropriate permissions
Streak Analytics – Track current and longest streaks with visual progress bars
Heatmap Visualization - GitHub-style heatmap showing 4 weeks of habit completions
Predefined Habit Templates – 7 ready-to-use habits for new users
Predefined Habits with 4 weeks test data

2.  Features
Core Features 
   Feature	                                      Description
a. User Management	                  Register, login, and role-based access control
b. Habit Management	                  Create, complete, delete, and view habits
c. Streak Tracking	                  Calculate current and longest streaks
d. Heatmap Visualization	          Visual representation of habit completions
e. Guest Mode	                      Demo account with pre-populated habits
f. Admin Dashboard	                  View all users and habits

Analytics Features
Features	
- Current Streak checks for	Consecutive days/weeks/months from today
- Longest Streak checks for Best streak ever achieved
- Progress Tracking; Visual progress bars toward targets
- Periodicity Filter for filtering habits by daily/weekly/monthly
- Struggling Habits	Identify checks for habits with < 50% completion rate

3. Tech Stack
Category	    Technology	    Version

- Language	    Python	        3.10+
- Database	    SQLite	        Built-in
- CLI Framework	Questionary	    2.0.1
- Testing	        Pytest 	        9.1.1 
- Code Quality	Ruff	        Latest
- Formatting	    Black	        Latest

4. Installation

Prerequisites
- Python 3.10 or higher

Step 1: Clone the Repository
git clone https://github.com/MaryAnyagafuOkafor/habit-tracker.git
cd habit-tracker

Step 2: Install Dependencies
pip install -r requirements.txt

Step 3: Initialize Database
# Run the app (it will create the database automatically)
python main.py

Step 4: Load Seed Data (Optional)
# Load predefined habits with 4 weeks of test data
python scripts/seed_data.py

🎯 Quick Start
Run the Application
python main.py

**First-Time User Flow**

- Register a new account
- Login with your credentials
- Create your first habit/choose from predefined templates
- Complete habits daily/weekly/monthly
- View your streaks and heatmap
- Track your progress

5. Project Structure

habit-tracker/
│
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Project configuration
├── pytest.ini                   # Pytest configuration
├── ruff.toml                    # Ruff linter configuration
│
├── src/                         # Source code
│   ├── core/                    # Core business logic (4-Layer Architecture)
│   │   ├── presentation/        # Layer 1: CLI Interface
│   │   │   └── user_interface.py
│   │   ├── services/            # Layer 2: Business Logic (Orchestration)
│   │   │   └── habit_service.py
│   │   ├── models/              # Layer 3: Domain Models (Entities & rules)
│   │   │   ├── habit.py
│   │   │   └── user.py
│   │   └── database/            # Layer 4: Data Access (Database Operations & CRUD)
│   │       └── repository.py
│   │
│   ├── analytics/               # Functional Programming Module
│   │   ├── streak.py            # Streak calculations (pure functions)
│   │   └── heatmap.py           # Heatmap generation
│   │
│   └── utils/                   # Cross-cutting utilities
│       ├── helpers.py           # Shared helper functions
│       └── predefined_habits.py # Habit templates
│
├── tests/                       # Test suite
│   ├── conftest.py              # Shared fixtures
│   ├── unit/                    # Unit tests
│   │   ├── analytics/           # Analytics tests
│   │   ├── models/              # Model tests
│   │   └── services/            # Service tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
│
├── scripts/                     # Utility scripts
│   ├── seed_data.py             # Seed data generator
│
└── data/                        # Data directory
    └── habits.db                # SQLite database

6. Architecture Principles

Principle	                        Description
Single Responsibility	      Each module has one clear purpose
Separation of Concerns	      OOP for state, FP for calculations
Dependency Inversion	      Services depend on abstractions
Pure Functions	              Analytics are side-effect free
Testability	                  Each layer can be tested independently

7.  User Guide
Authentication
Menu Option	              Description
🔑 Login	        Login with existing credentials
📝 Register	        Create a new account
👤 Guest Login	    Demo account with pre-populated habits
👑 Admin Login	    Access administrative features
🚪 Exit	            Exit the application

User Menu
Menu Option	                 Description
📋 View My Habits	  List all your habits with streak info
➕ Create Habit	      Create a habit (template or custom)
✅ Complete Habit	  Mark a habit as complete for today
🗑️ Delete Habit	      Remove a habit (soft delete)
📊 View Heatmap	      Display 4-week completion heatmap
📈 View Dashboard	  Show comprehensive analytics
🚪 Logout	          Logout of the application

Guest Menu
Menu Option	                        Description
📈 Guest Dashboard	         Analytics menu (read-only)
🔥 View Heatmap	             View guest habits heatmap
🔑 Login to Main Account	 Navigate to login

8. Database Schema
- Users Table
Column	          Type	                     Description
user_id	        TEXT (PK)	            Unique user identifier
username	    TEXT (UNIQUE)	        User's username
email	        TEXT	                User's email address
password_hash	TEXT	                Argon2 hashed password
role	        TEXT	                'admin', 'user', or 'guest'
is_active	    INTEGER	                1 = active, 0 = inactive
created_at	    TEXT	                Creation timestamp
- Habits Table
Column	                     Type                                    Description
habit_id	               TEXT (PK)	                        Unique habit identifier
user_id	                   TEXT (FK)	                        Owner's user ID
name	                   TEXT	                                Habit name
description	               TEXT	                                Optional description
periodicity	               TEXT	                                'daily', 'weekly', or 'monthly'
is_active	               INTEGER	                            1 = active, 0 = inactive
created_at	               TEXT	                                Creation timestamp
- Habit Completions Table
Column	                      Type	                       Description
completion_id	            INTEGER (PK)	            Auto-incrementing ID
habit_id	                TEXT (FK)	                Parent habit ID
completion_date	            TEXT	                    Date/time of completion
created_at	                TEXT	                    Record creation timestamp

9. Testing
Run all tests:
python -m pytest -v

Run specific tests:
# unit tests
python -m pytest tests/unit/ -v

# integration tests
python -m pytest tests/integration/ -v

# E2E tests
python -m pytest tests/e2e/ -v

Run with coverage
# Coverage summary
python -m pytest --cov=src -v

10. Development
Code Quality Tools
# Lint code
python -m ruff check src/ tests/

# Auto-fix issues
python -m ruff check --fix src/ tests/

# Format code
python -m black src/ tests/

# Run all checks
python -m ruff check --fix src/ tests/ && black src/ tests/

Database
# delete the database
del data\habits.db
