# src/utils/predefined_habits.py

"""
PREDEFINED HABIT TEMPLATES
============================

This module provides predefined habit templates that users can choose from
when creating new habits. These are NOT stored in the database - they are
just suggestions/templates.

The templates are organized by periodicity:
    - Daily habits (3)
    - Weekly habits (2)
    - Monthly habits (2)
    Total: 7 habits
"""

from typing import List, Dict

# ============================================
# PREDEFINED HABIT TEMPLATES
# ============================================

PREDEFINED_HABITS = [
    # Daily habits (3)
    {
        "name": "Morning Exercise",
        "description": "30 minutes of physical activity",
        "periodicity": "daily",
        "category": "health",
    },
    {
        "name": "Read Daily",
        "description": "Read 20 pages of a book",
        "periodicity": "daily",
        "category": "learning",
    },
    {
        "name": "Meditate",
        "description": "10 minutes of mindfulness meditation",
        "periodicity": "daily",
        "category": "wellness",
    },
    # Weekly habits (2)
    {
        "name": "Clean the House",
        "description": "Thorough house cleaning",
        "periodicity": "weekly",
        "category": "chores",
    },
    {
        "name": "Weekly Review",
        "description": "Plan and review the week ahead",
        "periodicity": "weekly",
        "category": "productivity",
    },
    # Monthly habits (2)
    {
        "name": "Financial Check",
        "description": "Review budget and finances",
        "periodicity": "monthly",
        "category": "finance",
    },
    {
        "name": "Skill Development",
        "description": "Complete a course or learn a new skill",
        "periodicity": "monthly",
        "category": "learning",
    },
]


def get_predefined_habits() -> List[Dict[str, str]]:
    """Return all predefined habit templates."""
    return PREDEFINED_HABITS.copy()


def get_habits_by_periodicity(periodicity: str) -> List[Dict[str, str]]:
    """Filter predefined habits by periodicity."""
    valid = {"daily", "weekly", "monthly"}
    if periodicity not in valid:
        raise ValueError(f"Invalid periodicity: {periodicity}")
    return [h for h in PREDEFINED_HABITS if h["periodicity"] == periodicity]
