"""Steps data."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, shemas
from filetransferautomation.database import SessionLocal
from filetransferautomation.models import Step

router = APIRouter()


def get_step(step_id: int) -> models.Step | None:
    """Get a step."""
    with SessionLocal() as db:
        db_step = (
            db.query(models.Step).filter(models.Step.step_id == step_id).one_or_none()
        )
        if db_step:
            db_step.host = (
                db.query(models.Host)
                .filter(models.Host.host_id == db_step.host_id)
                .all()
            )
        if not db_step:
            raise HTTPException(status_code=404, detail="step not found")
        return db_step


@router.get("/active")
def get_active_steps():
    """Get all active steps."""
    with SessionLocal() as db:
        result = db.query(models.Step).filter(models.Step.active == 1).all()
        return result


@router.get("")
async def get_steps():
    """Get all steps."""
    with SessionLocal() as db:
        result = db.query(models.Step).all()
        return result


@router.post("", status_code=201)
async def add_step(step: shemas.AddStep):
    """Add a step."""
    with SessionLocal() as db:
        db_step = Step(**step.dict())
        db.add(db_step)
        db.commit()
        db.refresh(db_step)
        return db_step


@router.put("/{step_id}")
async def update_step(step_id: int, step: shemas.AddStep):
    """Update a step."""
    with SessionLocal() as db:
        db_step = db.query(Step).filter(Step.step_id == step_id)
        if not db_step:
            raise HTTPException(status_code=404, detail="step not found")
        if db_step:
            db_step.update(dict(step))
            db.commit()
            db_step = db.query(Step).filter(Step.step_id == step_id).one_or_none()
            return db_step
        return None


@router.delete("/{step_id}", status_code=204)
async def delete_step(step_id: int):
    """Delete a step."""
    with SessionLocal() as db:
        db_step = db.query(Step).filter(Step.step_id == step_id)
        if not db_step:
            raise HTTPException(status_code=404, detail="step not found")
        if db_step:
            db_step.delete()
            db.commit()
        return None
