"""
HABIT TRACKER - Application Entry Point
========================================

This is the main entry point for the Habit Tracker application.
It initializes the user interface and starts the application.

Usage:
    python main.py

Example:
    $ python main.py
    🚀 Starting Habit Tracker...
    👋 Welcome to Habit Tracker!
    ...
"""

import sys
import os

# Add the project root to Python path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.user_interface import UserInterface


def main():
    """
    Application entry point.

    This function:
        1. Displays a startup message
        2. Creates an instance of the UserInterface
        3. Starts the main application loop via run()
    """
    print("\n" + "=" * 50)
    print("🚀 HABIT TRACKER")
    print("=" * 50)
    print("Your personal habit tracking assistant")
    print("Track daily, weekly, and monthly habits")
    print("View streaks, analytics, and heatmaps")
    print("=" * 50 + "\n")

    try:
        cli = UserInterface()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Habit Tracker.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your database connection and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
