"""Schedules data."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, shemas
from filetransferautomation.database import SessionLocal
from filetransferautomation.models import Schedule

router = APIRouter()


@router.get("/{schedule_id}")
def get_schedule(schedule_id: int):
    """Get a schedules."""
    with SessionLocal() as db:
        result = (
            db.query(models.Schedule)
            .filter(models.Schedule.schedule_id == schedule_id)
            .one_or_none()
        )
        return result


@router.get("")
def get_schedules():
    """Get all schedules."""
    with SessionLocal() as db:
        result = db.query(models.Schedule).all()
        return result


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: int):
    """Delete a schedule."""
    with SessionLocal() as db:
        db_schedule = db.query(models.Schedule).filter(
            models.Schedule.schedule_id == schedule_id
        )
        if not db_schedule:
            raise HTTPException(status_code=404, detail="schedule not found")
        if db_schedule:
            db_schedule.delete()
            db.commit()
        return None


@router.post("", status_code=201)
async def add_schedule(schedule: shemas.AddSchedule):
    """Add a schedule."""
    with SessionLocal() as db:
        db_task = models.Schedule(**schedule.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task


@router.put("/{schedule_id}")
async def update_schedule(schedule_id: int, schedule: shemas.AddSchedule):
    """Update a schedule."""
    with SessionLocal() as db:
        db_schedule = (
            db.query(Schedule).filter(Schedule.schedule_id == schedule_id).one_or_none()
        )
        if not db_schedule:
            raise HTTPException(status_code=404, detail="schedule not found")
        if db_schedule:
            db.query(Schedule).filter(Schedule.schedule_id == schedule_id).update(
                dict(schedule)
            )
            db.commit()
            db_schedule = (
                db.query(Schedule)
                .filter(Schedule.schedule_id == schedule_id)
                .one_or_none()
            )
            return db_schedule
        return None


async def update_schedule_job_id(schedule_id: int, scheduler_job_id: int):
    """Update a schedule and set scheduler_job_id."""
    with SessionLocal() as db:
        db_schedule = (
            db.query(Schedule).filter(Schedule.schedule_id == schedule_id).one_or_none()
        )
        if db_schedule:
            db_schedule.scheduler_job_id = scheduler_job_id
            db.commit()
            return db_schedule
        return None
