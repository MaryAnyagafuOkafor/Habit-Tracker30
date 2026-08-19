# src/analytics/heatmap.py

import calendar
from datetime import datetime, timedelta
from typing import Dict, Any, List

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

    def _get_month_calendar(self) -> List[List]:
        """
        Get the current month's calendar as a grid.

        Returns:
            List of weeks, each week is a list of (day_number, date_object, is_completed)
        """
        today = datetime.now().date()
        year = today.year
        month = today.month

        # Get the month calendar
        cal = calendar.monthcalendar(year, month)

        # Build completion set for quick lookup
        completion_set = {c.date() for c in self.completion_dates}

        # Build the grid with date objects
        month_grid = []
        for week in cal:
            week_data = []
            for day_num in week:
                if day_num == 0:
                    # Empty cell (day from previous/next month)
                    week_data.append({"day": None, "date": None, "completed": False})
                else:
                    date_obj = datetime(year, month, day_num).date()
                    week_data.append({
                        "day": day_num,
                        "date": date_obj,
                        "completed": date_obj in completion_set
                    })
            month_grid.append(week_data)

        return month_grid

    def show(self) -> str:
        """
        Generate and return the heatmap as a string.

        Returns:
            String representation of the heatmap
        """
        if not self.completion_dates:
            return "📊 No completions yet. Start building your habit streak! 💪"

        today = datetime.now().date()
        month_name = today.strftime("%B %Y")

        # Get the month calendar
        month_grid = self._get_month_calendar()

        # Build the heatmap
        lines = ["=" * 60, f"📊 HABIT HEATMAP — {month_name}", f"   Habit: {self.habit.name}", "=" * 60, ""]

        # Days of the week header
        days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header = "     " + "  ".join(f"{d:>3}" for d in days_abbr)
        lines.append(header)
        lines.append("     " + "-" * 27)

        # Generate weeks with week numbers
        week_num = 1
        for week_data in month_grid:
            # Skip completely empty weeks (shouldn't happen but just in case)
            if not any(w["day"] is not None for w in week_data):
                continue

            # Build the week row
            week_row = []
            day_labels = []

            for cell in week_data:
                if cell["day"] is None:
                    week_row.append("    ")  # Empty cell (3 spaces + 1 padding)
                    day_labels.append("    ")
                else:
                    # Mark with ██ if completed, otherwise ░░
                    symbol = "██" if cell["completed"] else "░░"
                    # Add day number as tiny text (optional - uncomment if you want)
                    # day_str = f"{cell['day']:2d}"
                    # week_row.append(f"{symbol}{day_str}")
                    week_row.append(f"  {symbol} ")
                    day_labels.append(f"{cell['day']:3d} ")

            # Add week label and the row
            week_label = f"Week {week_num:2d}:"
            lines.append(f"{week_label} " + "".join(week_row))

            # OPTIONAL: Show day numbers below the symbols (uncomment to enable)
            # lines.append(f"       " + "".join(day_labels))
            # lines.append("")

            week_num += 1

        lines.append("")
        lines.append("-" * 60)

        # Stats
        total = self.get_completion_count()
        streak = self.get_current_streak()

        # Calculate completion percentage for this month
        total_days_in_month = sum(1 for week in month_grid for cell in week if cell["day"] is not None)
        days_completed = sum(1 for week in month_grid for cell in week if cell["completed"])

        if total_days_in_month > 0:
            completion_rate = (days_completed / total_days_in_month) * 100
            lines.append(f"📈 Total completions: {total}")
            lines.append(f"🔥 Current streak:    {streak} days")
            lines.append(
                f"📅 This month:        {days_completed}/{total_days_in_month} days completed ({completion_rate:.0f}%)")
        else:
            lines.append(f"📈 Total completions: {total}")
            lines.append(f"🔥 Current streak:    {streak} days")

        # Legend
        lines.append("")
        lines.append("Legend:")
        lines.append("  ██ = Completed on that day")
        lines.append("  ░░ = Not completed on that day")
        lines.append("  (empty spaces = days from other months)")

        lines.append("")
        lines.append("=" * 60)
        lines.append(f"💡 Tip: Today is {today.strftime('%A, %B %d, %Y')}")

        return "\n".join(lines)

    def show_compact(self) -> str:
        """
        Generate a compact version of the heatmap (like the original but with dates).

        Returns:
            String representation of the heatmap
        """
        if not self.completion_dates:
            return "📊 No completions yet. Start building your habit streak! 💪"

        now = datetime.now()
        start_date = now - timedelta(days=27)
        completion_set = {c.date() for c in self.completion_dates}

        lines = ["📊 Habit Heatmap (Last 28 Days)", "=" * 50, ""]

        # Days of the week header
        days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        lines.append("     " + " ".join(days_abbr))
        lines.append("     " + "-" * 27)

        # Generate 4 weeks
        for week in range(4):
            week_days = []
            date_labels = []

            for day in range(7):
                current_date = start_date + timedelta(days=week * 7 + day)
                date_str = current_date.strftime("%d")  # Day of month

                if current_date.date() in completion_set:
                    week_days.append("██")
                else:
                    week_days.append("░░")

                date_labels.append(f"{date_str:2s}")

            # Calculate week range
            week_start = start_date + timedelta(days=week * 7)
            week_end = week_start + timedelta(days=6)
            # noinspection PyUnusedLocal
            week_range = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"

            # Add week with date range
            week_label = f"Week {week + 1}:"
            lines.append(f"{week_label:<7} " + " ".join(week_days))
            lines.append(f"        " + " ".join(date_labels))
            lines.append("")

        lines.append("")
        lines.append(f"📈 Total completions: {self.get_completion_count()}")
        lines.append(f"🔥 Current streak: {self.get_current_streak()} days")
        lines.append("")
        lines.append("Legend: ██ = Completed  ░░ = Not completed")
        lines.append(f"📅 Today: {datetime.now().strftime('%A, %B %d, %Y')}")

        return "\n".join(lines)