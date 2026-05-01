"""
pawpal_system.py — Core scheduling logic for PawPal+
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

PRIORITY_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}


@dataclass
class Task:
    name: str
    start_time: datetime
    duration_minutes: int
    priority: str  # HIGH, MEDIUM, LOW
    pet_name: str = "Unknown"
    recurring: Optional[str] = None  # "daily" | "weekly" | None

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task overlaps with another."""
        return self.start_time < other.end_time and self.end_time > other.start_time

    def priority_rank(self) -> int:
        return PRIORITY_RANK.get(self.priority.upper(), 0)

    def __str__(self):
        t = self.start_time.strftime("%I:%M %p")
        return f"{t} — {self.name} ({self.duration_minutes} min) [{self.priority}] | {self.pet_name}"


def parse_task(
    name: str,
    start_str: str,
    duration_minutes: int,
    priority: str,
    pet_name: str = "Unknown",
    recurring: Optional[str] = None,
    date_str: str = None,
) -> Task:
    """Parse and validate a task from raw inputs."""
    if not name or not name.strip():
        raise ValueError("Task name cannot be empty.")
    if duration_minutes <= 0:
        raise ValueError(f"Duration must be positive. Got: {duration_minutes}")
    if priority.upper() not in PRIORITY_RANK:
        raise ValueError(f"Priority must be HIGH, MEDIUM, or LOW. Got: {priority}")

    date_prefix = date_str or datetime.today().strftime("%Y-%m-%d")
    try:
        start_time = datetime.strptime(f"{date_prefix} {start_str}", "%Y-%m-%d %I:%M %p")
    except ValueError:
        try:
            start_time = datetime.strptime(f"{date_prefix} {start_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(f"Could not parse start time: '{start_str}'. Use '8:00 AM' or '08:00'.")

    logger.info("Parsed task: %s at %s [%s]", name, start_time, priority)
    return Task(
        name=name.strip(),
        start_time=start_time,
        duration_minutes=duration_minutes,
        priority=priority.upper(),
        pet_name=pet_name.strip(),
        recurring=recurring,
    )


def expand_recurring(tasks: List[Task], days: int = 7) -> List[Task]:
    """Expand recurring tasks into individual instances over N days."""
    expanded = []
    today = datetime.today().date()

    for task in tasks:
        if task.recurring is None:
            expanded.append(task)
            continue

        for i in range(days):
            candidate_date = today + timedelta(days=i)
            if task.recurring == "daily":
                new_start = task.start_time.replace(
                    year=candidate_date.year,
                    month=candidate_date.month,
                    day=candidate_date.day,
                )
                expanded.append(Task(
                    name=task.name,
                    start_time=new_start,
                    duration_minutes=task.duration_minutes,
                    priority=task.priority,
                    pet_name=task.pet_name,
                    recurring=task.recurring,
                ))
            elif task.recurring == "weekly":
                if candidate_date.weekday() == task.start_time.weekday():
                    new_start = task.start_time.replace(
                        year=candidate_date.year,
                        month=candidate_date.month,
                        day=candidate_date.day,
                    )
                    expanded.append(Task(
                        name=task.name,
                        start_time=new_start,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        pet_name=task.pet_name,
                        recurring=task.recurring,
                    ))

    logger.info("Expanded %d tasks to %d instances.", len(tasks), len(expanded))
    return expanded


def sort_by_priority(tasks: List[Task]) -> List[Task]:
    """Sort tasks by priority (HIGH first), then by start time."""
    return sorted(tasks, key=lambda t: (-t.priority_rank(), t.start_time))


def detect_and_resolve_conflicts(tasks: List[Task]) -> tuple[List[Task], List[dict]]:
    """
    Greedily resolve conflicts. Higher-priority tasks are kept.
    Returns (schedule, removed_log).
    """
    sorted_tasks = sort_by_priority(tasks)
    schedule: List[Task] = []
    removed: List[dict] = []

    for candidate in sorted_tasks:
        conflict = next((t for t in schedule if candidate.conflicts_with(t)), None)
        if conflict:
            logger.warning(
                "Conflict: '%s' [%s] overlaps '%s' [%s]. Removing '%s'.",
                candidate.name, candidate.priority,
                conflict.name, conflict.priority,
                candidate.name,
            )
            removed.append({"task": candidate, "reason": f"conflict with '{conflict.name}'"})
        else:
            schedule.append(candidate)

    schedule.sort(key=lambda t: t.start_time)
    logger.info("Schedule built: %d tasks kept, %d removed.", len(schedule), len(removed))
    return schedule, removed


def build_schedule(tasks: List[Task]) -> tuple[List[Task], List[dict]]:
    """Full pipeline: expand recurrence → resolve conflicts → return schedule."""
    if not tasks:
        logger.warning("No tasks provided to scheduler.")
        return [], []
    expanded = expand_recurring(tasks)
    return detect_and_resolve_conflicts(expanded)


def print_schedule(schedule: List[Task], removed: List[dict]) -> None:
    """Pretty-print the final schedule and any removed tasks."""
    print("\n── PawPal+ Daily Schedule ──────────────────")
    if not schedule:
        print("  (no tasks scheduled)")
    for task in schedule:
        print(f"  ✅ {task}")
    if removed:
        print("\n── Removed due to conflicts ─────────────────")
        for entry in removed:
            print(f"  ⚠️  {entry['task'].name} — {entry['reason']}")
    print("─────────────────────────────────────────────\n")
