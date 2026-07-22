# src/analytics/heatmap.py

from datetime import datetime, timedelta
from typing import Dict, Any

from src.core.models.habit import Habit


class HabitHeatmap:
    """Generate GitHub-style heatmap for habit completions."""

    def __init__(self, habit: Habit):
        """
        Initialize the heatmap with a habit.

        Args:
            habit: Habit object to generate heatmap for
        """
        self.habit = habit
        self.completion_dates = habit.completions.copy() if habit.completions else []

    def get_completion_count(self) -> int:
        """Get total number of completions."""
        return len(self.completion_dates)

    def get_current_streak(self) -> int:
        """Get current streak from completions."""
        if not self.completion_dates:
            return 0

        sorted_dates = sorted(self.completion_dates, reverse=True)
        streak = 0
        current_date = datetime.now().date()

        for completion in sorted_dates:
            completion_date = completion.date()
            if completion_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif completion_date < current_date:
                break

        return streak

    def get_week_stats(self) -> Dict[str, Any]:
        """Get statistics for the current week (last 7 days including today)."""
        today = datetime.now().date()
        week_start = today - timedelta(days=6)  # 7 days including today

        completion_dates = {c.date() for c in self.completion_dates}

        days = []
        total = 0

        for i in range(7):
            day = week_start + timedelta(days=i)
            completed = day in completion_dates
            days.append({"date": day, "completed": completed})
            if completed:
                total += 1

        return {"total": total, "days": days, "streak": self.get_current_streak()}

    def show(self) -> str:
        """
        Generate and return the heatmap as a string.

        Returns:
            String representation of the heatmap
        """
        if not self.completion_dates:
            return "📊 No completions yet. Start building your habit streak! 💪"

        # Get dates for the last 4 weeks (28 days)
        now = datetime.now()
        start_date = now - timedelta(days=27)

        # Build completion set for quick lookup
        completion_set = {c.date() for c in self.completion_dates}

        # Build the heatmap
        lines = ["📊 Habit Heatmap", "=" * 50, ""]

        # Days of the week header
        days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        lines.append("     " + " ".join(days_abbr))

        # Generate 4 weeks of data
        for week in range(4):
            week_days = []
            for day in range(7):
                current_date = start_date + timedelta(days=week * 7 + day)
                if current_date.date() in completion_set:
                    week_days.append("██")  # Completed
                else:
                    week_days.append("░░")  # Not completed

            # Add week label
            week_label = f"Week {week + 1}:"
            lines.append(f"{week_label} " + " ".join(week_days))

        lines.append("")
        lines.append(f"📈 Total completions: {self.get_completion_count()}")
        lines.append(f"🔥 Current streak: {self.get_current_streak()} days")

        # Add legend
        lines.append("")
        lines.append("Legend: ██ = Completed  ░░ = Not completed")

        return "\n".join(lines)
