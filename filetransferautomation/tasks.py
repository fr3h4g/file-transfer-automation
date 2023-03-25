"""Tasks api."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Literal

from fastapi import APIRouter

# import pymysql
import pymysql.cursors

from filetransferautomation.settings import MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_USER

router = APIRouter()


@dataclass
class Step:
    """Task Step."""

    host_id: int
    step_type: Literal["source"] | Literal["process"] | Literal["destination"]
    type: str
    directory: str | None = ""
    file_mask: str | None = ""
    filename: str | None = ""
    username: str | None = ""
    password: str | None = ""
    unc_share: str | None = ""
    share: str | None = ""


@dataclass
class Schedule:
    """Task Schedule."""

    cron: str


@dataclass
class Task:
    """Task."""

    id: int
    name: str
    schedules: list[Schedule]
    steps: list[Step]
    description: str
    active: int


def load_tasks() -> list[Task]:
    """Load tasks from database."""
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    tasks = []

    with connection and connection.cursor() as cursor:
        sql = "SELECT * FROM tasks"
        cursor.execute(sql, ())
        result = cursor.fetchall()
        for row in result:
            tmp = json.loads(row["steps"])
            steps = []
            for step in tmp:
                steps.append(Step(**step))
            row["steps"] = steps

            tmp = json.loads(row["schedules"])
            schedules = []
            for schedule in tmp:
                schedules.append(Schedule(**schedule))
            row["schedules"] = schedules

            tasks.append(Task(**row))
    return tasks


@router.get("", response_model=list[Task])
async def get_tasks():
    """Get all tasks."""
    return load_tasks()
