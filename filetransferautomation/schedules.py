"""Schedules data."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Schedule:
    """Schedule dataclass."""

    schedule_id: int
    task_id: int
    cron: str


SCHEDULES: list[Schedule] = []


def load_schedules() -> list[Schedule]:
    """Load schedules from database."""
    global SCHEDULES
    SCHEDULES.append(Schedule(schedule_id=1, task_id=1, cron="*/1 * * * *"))
    return SCHEDULES


def get_schedules(task_id: int) -> list[Schedule]:
    """Get all schedules for a task."""
    return_data = []
    for schedule in SCHEDULES:
        if schedule.task_id == task_id:
            return_data.append(schedule)
    return return_data
