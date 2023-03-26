from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Schedule:
    schedule_id: int
    task_id: int
    cron: str


SCHEDULES: list[Schedule] = []


def load_schedules() -> list[Schedule]:
    global SCHEDULES
    SCHEDULES.append(Schedule(schedule_id=1, task_id=1, cron="*/1 * * * *"))
    return SCHEDULES


def get_schedules(task_id: int) -> list[Schedule]:
    return_data = []
    for schedule in SCHEDULES:
        if schedule.task_id == task_id:
            return_data.append(schedule)
    return return_data
