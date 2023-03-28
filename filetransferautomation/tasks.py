"""Tasks api and data."""
from __future__ import annotations

from fastapi import APIRouter

# from filetransferautomation import hosts
# from filetransferautomation.hosts import Host, get_host
from filetransferautomation.schedules import get_schedules

# from filetransferautomation.settings import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER
from filetransferautomation.steps import get_steps
from filetransferautomation.models import Task

# import json
# from typing import Literal


# import pymysql.cursors


router = APIRouter()


TASKS: list[Task] = []


def load_tasks() -> list[Task]:
    """Load tasks from database."""
    global TASKS

    TASKS = []
    TASKS.append(
        Task(
            task_id=1,
            name="Local copy test",
            schedules=get_schedules(task_id=1),
            steps=get_steps(task_id=1),
            description="",
            active=1,
        )
    )
    # connection = pymysql.connect( # type: ignore
    #     host=MYSQL_HOST,
    #     user=MYSQL_USER,
    #     password=MYSQL_PASS,
    #     database=MYSQL_DB,
    #     charset="utf8mb4",
    #     cursorclass=pymysql.cursors.DictCursor,
    # )

    # with connection and connection.cursor() as cursor:
    #     sql = "SELECT * FROM tasks"
    #     cursor.execute(sql, ())
    #     result = cursor.fetchall()
    #     for row in result:
    #         tmp = json.loads(row["steps"])
    #         steps = []
    #         for step in tmp:
    #             steps.append(Step(**step))
    #         row["steps"] = steps

    #         tmp = json.loads(row["schedules"])
    #         schedules = []
    #         for schedule in tmp:
    #             schedules.append(Schedule(**schedule))
    #         row["schedules"] = schedules

    #         TASKS.append(Task(**row))
    return TASKS


def get_task(task_id: int) -> Task | None:
    """Get a task."""
    for task in TASKS:
        if task.task_id == task_id:
            return task
    return None


@router.get("", response_model=list[Task])
async def get_tasks():
    """Get all tasks."""
    return load_tasks()
