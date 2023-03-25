from __future__ import annotations
from typing import Literal, Optional
from dataclasses import dataclass
from fastapi import APIRouter
from pydantic import BaseModel
import json

# import pymysql
import pymysql.cursors

from filetransferautomation.settings import MYSQL_DB, MYSQL_HOST, MYSQL_USER, MYSQL_PASS

router = APIRouter()


@dataclass
class Step:
    host_id: int
    step_type: Literal["source"] | Literal["process"] | Literal["destination"]
    type: str
    directory: Optional[str] = ""
    file_mask: Optional[str] = ""
    filename: Optional[str] = ""
    username: Optional[str] = ""
    password: Optional[str] = ""
    unc_share: Optional[str] = ""
    share: Optional[str] = ""


@dataclass
class Schedule:
    cron: str


@dataclass
class Task:
    id: int
    name: str
    schedules: list[Schedule]
    steps: list[Step]
    description: str
    active: int


def load_tasks() -> list[Task]:
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
    return load_tasks()
