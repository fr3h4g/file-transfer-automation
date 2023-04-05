"""Tasks api and data."""
from __future__ import annotations

import logging
import os
import pathlib
import subprocess
import sys
import threading
import uuid

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, settings, shemas, tasks
from filetransferautomation.database import SessionLocal
from filetransferautomation.hosts import get_host
from filetransferautomation.logs import add_task_log_entry
from filetransferautomation.models import Task
from filetransferautomation.plugin_collection import PluginCollection
from filetransferautomation.transfer import Transfer

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

    variables = {"workspace_id": workspace_id}

    for step in task.steps:
        for plugin in step_plugins.plugins:
            if step.script.lower() == plugin.name.lower():
                tmp = plugin(step.arguments, variables)
                tmp.process()

    logging.info(
        f"Task '{task.name}', id: {task.task_id}, task_id: {workspace_id} completed."
    )
    logging.info(
        f"--- Exiting task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id}, "
        f"thread {threading.get_native_id()}."
    )
    add_task_log_entry(workspace_id, task.task_id, "success")


def run_task_old(task: models.Task):
    """Run task."""
    task_run_id = str(uuid.uuid4())
    logging.info(
        f"--- Running task '{task.name}', id: {task.task_id}, task_run_id: {task_run_id}, "
        f"thread {threading.get_native_id()}."
    )
    add_task_log_entry(task_run_id, task.task_id, "running")
    work_directory = os.path.join(settings.WORK_DIR, task_run_id)
    os.mkdir(work_directory)
    downloaded_files = []
    for step in task.steps:
        if step.host and step.step_type == "source" and step.host.type:
            transfer = Transfer(
                step.host.type, "download", task, step, work_directory, task_run_id
            )
            downloaded_files = transfer.run()
    for step in task.steps:
        if step.step_type == "process" and step.process and step.process.script_file:
            script_dir = pathlib.Path(settings.SCRIPTS_DIR).resolve()
            work_dir = pathlib.Path(work_directory).resolve()
            if step.process.per_file == 1:
                for file in downloaded_files:
                    subprocess.call(
                        sys.executable
                        + " "
                        + os.path.join(script_dir, step.process.script_file)
                        + " "
                        + file.name,
                        shell=True,
                        cwd=work_dir,
                    )
            else:
                subprocess.call(
                    sys.executable
                    + " "
                    + os.path.join(script_dir, step.process.script_file),
                    shell=True,
                    cwd=work_dir,
                )
    for step in task.steps:
        if step.host and step.step_type == "destination" and step.host.type:
            transfer = Transfer(
                step.host.type, "upload", task, step, work_directory, task_run_id
            )
            transfer.run()
    os.rmdir(work_directory)
    logging.info(
        f"Task '{task.name}', id: {task.task_id}, task_id: {task_run_id} completed."
    )
    logging.info(
        f"--- Exiting task '{task.name}', id: {task.task_id}, task_run_id: {task_run_id}, "
        f"thread {threading.get_native_id()}."
    )
    add_task_log_entry(task_run_id, task.task_id, "success")


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
