"""Tasks api and data."""
from __future__ import annotations

from fastapi import APIRouter

from filetransferautomation import models
from filetransferautomation.database import SessionLocal
from filetransferautomation.models import Task

router = APIRouter()


TASKS: list[Task] = []


def get_task(task_id: int) -> models.Task | None:
    """Get a task."""
    # for task in TASKS:
    #     if task.task_id == task_id:
    #         return task
    # return None
    db = SessionLocal()
    result = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    return result


def get_active_tasks() -> list[models.Task]:
    """Get a task."""
    # for task in TASKS:
    #     if task.task_id == task_id:
    #         return task
    # return None
    db = SessionLocal()
    result = db.query(models.Task).filter(models.Task.active == 1).all()
    # for row in result:
    # row.schedules = get_schedules(task_id=row.task_id)
    # row.steps = get_steps(task_id=row.task_id)
    return result


def get_all_tasks() -> list[models.Task]:
    """Get a task."""
    # for task in TASKS:
    #     if task.task_id == task_id:
    #         return task
    # return None
    db = SessionLocal()
    result = db.query(models.Task).all()
    # for row in result:
    # row.schedules = get_schedules(task_id=row.task_id)
    # row.steps = get_steps(task_id=row.task_id)
    return result


@router.get("")
async def get_tasks():
    """Get all tasks."""
    return get_all_tasks()
