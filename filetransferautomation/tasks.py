"""Tasks api and data."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, shemas
from filetransferautomation.database import SessionLocal
from filetransferautomation.models import Task

router = APIRouter()


@router.get("/{task_id}")
def get_task(task_id: int):
    """Get a task."""
    db = SessionLocal()
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    return db_task


@router.get("/active")
def get_active_tasks():
    """Get all active tasks."""
    db = SessionLocal()
    result = db.query(models.Task).filter(models.Task.active == 1).all()
    return result


@router.get("")
async def get_tasks():
    """Get all tasks."""
    db = SessionLocal()
    result = db.query(models.Task).all()
    return result


@router.post("", status_code=201)
async def add_task(task: shemas.AddTask):
    """Add a task."""
    db = SessionLocal()
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.put("/{task_id}")
async def update_task(task_id: int, task: shemas.AddTask):
    """Update a task."""
    db = SessionLocal()
    db_task = db.query(Task).filter(Task.task_id == task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    if db_task:
        db_task.update(dict(task))
        db.commit()
        db_task = db.query(Task).filter(Task.task_id == task_id).one_or_none()
        return db_task
    return None


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """Delete a task."""
    db = SessionLocal()
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    if db_task:
        db_task.delete()
        db.commit()
    return None


@router.get("/{task_id}/schedules")
def get_task_schedules(task_id: int):
    """Get a tasks schedules."""
    db = SessionLocal()
    db_task = db.query(models.Schedule).filter(models.Schedule.task_id == task_id).all()
    return db_task


@router.delete("/{task_id}/schedules/{schedule_id}", status_code=204)
async def delete_schedule(task_id: int, schedule_id: int):
    """Delete a schedule."""
    db = SessionLocal()
    db_schedule = db.query(models.Schedule).filter(
        models.Schedule.schedule_id == schedule_id,
        models.Schedule.task_id == task_id,
    )
    if not db_schedule:
        raise HTTPException(status_code=404, detail="schedule not found")
    if db_schedule:
        db_schedule.delete()
        db.commit()
    return None
