"""Tasks api and data."""
from __future__ import annotations

import logging
import os
import threading
import uuid

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, settings, shemas, tasks
from filetransferautomation.database import SessionLocal
from filetransferautomation.hosts import get_host
from filetransferautomation.logs import add_task_log_entry
from filetransferautomation.models import Task
from filetransferautomation.plugin_collection import PluginCollection


router = APIRouter()


def run_task(task: models.Task):
    """Run task."""
    workspace_id = str(uuid.uuid4())

    logging.info(
        f"--- Running task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id}, "
        f"thread {threading.get_native_id()}."
    )
    add_task_log_entry(workspace_id, task.task_id, "running")

    step_plugins = PluginCollection("filetransferautomation.step_plugins")

    variables = {
        "task_id": task.task_id,
        "task_name": task.name,
        "workspace_id": workspace_id,
        "workspace_directory": os.path.join(settings.WORK_DIR, workspace_id),
    }

    for step in task.steps:
        variables = {**variables, "step_id": step.step_id}
        plugin_found = False
        for plugin in step_plugins.plugins:
            if step.active == 0:
                logging.info(
                    f"Step is not active. Skipping step, step_id: {step.step_id}, "
                    f"script: {plugin.name.lower()}"
                )
            elif step.script.lower() == plugin.name.lower():
                plugin_found = True
                tmp = plugin(step.arguments, variables)
                tmp.process()
                variables = tmp.variables
        if not plugin_found:
            raise ValueError(f"Plugin script '{step.script.lower()}' not found.")

    logging.info(
        f"Task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id} completed."
    )
    logging.info(
        f"--- Exiting task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id}, "
        f"thread {threading.get_native_id()}."
    )
    add_task_log_entry(workspace_id, task.task_id, "success")


def run_task_threaded(task: tasks.Task):
    """Run task in thread."""
    new_thread = threading.Thread(target=run_task, args=(task,))
    new_thread.start()


@router.get("/{task_id}")
async def get_task(task_id: int):
    """Get a task."""
    db = SessionLocal()
    db_task = db.query(models.Task).filter(models.Task.task_id == task_id).one_or_none()
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    db_task.schedules = await get_task_schedules(db_task.task_id)
    db_task.steps = await get_task_steps(db_task.task_id)
    return db_task


@router.get("/active")
async def get_active_tasks():
    """Get all active tasks."""
    db = SessionLocal()
    result = db.query(models.Task).filter(models.Task.active == 1).all()
    for row in result:
        row.schedules = await get_task_schedules(row.task_id)
        row.steps = await get_task_steps(row.task_id)
    return result


@router.get("")
async def get_tasks():
    """Get all tasks."""
    db = SessionLocal()
    result = db.query(models.Task).all()
    for row in result:
        row.schedules = await get_task_schedules(row.task_id)
        row.steps = await get_task_steps(row.task_id)
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


@router.get("/{task_id}/steps")
async def get_task_steps(task_id: int):
    """Get all tasks steps."""
    db = SessionLocal()
    result = (
        db.query(models.Step)
        .filter(models.Step.task_id == task_id)
        .order_by(models.Step.sort_order)
        .all()
    )
    for row in result:
        if row.host_id:
            row.host = get_host(row.host_id)
    return result


@router.get("/{task_id}/schedules")
async def get_task_schedules(task_id: int):
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


@router.post("/{task_id}/run")
async def run_task_now(task_id: int):
    """Run a task."""
    db_task = await get_task(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    run_task_threaded(db_task)
    return None
