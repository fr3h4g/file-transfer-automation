"""Tasks api and data."""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import threading
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import and_
from sqlalchemy.sql.functions import func

from filetransferautomation import models, settings, shemas
from filetransferautomation.database import SessionLocal
from filetransferautomation.hosts import get_host
from filetransferautomation.logs import add_step_log_entry, add_task_log_entry
from filetransferautomation.models import FileLog, Task, TaskLog
from filetransferautomation.plugin_collection import PluginCollection

router = APIRouter()


def run_task(task_id: int):
    """Run task."""

    task = asyncio.run(get_task(task_id))

    workspace_id = str(uuid.uuid4())

    if task:
        if task.active == 0:
            logging.info(
                f"--- Task '{task.name}' is not active, skipping task, id: {task.task_id}"
            )
            return None

        error = False

        logging.info(
            f"--- Running task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id}, "
            f"thread {threading.get_native_id()}."
        )
        add_task_log_entry(workspace_id, task.task_id, "running")

        step_plugins = PluginCollection("filetransferautomation.step_plugins")

        global_variables = {
            "task_id": task.task_id,
            "task_name": task.name,
            "task": task,
            "workspace_id": workspace_id,
            "workspace_directory": os.path.join(settings.WORK_DIR, workspace_id),
        }
        logging.debug(f"{global_variables=}")

        variables = {}

        create_workspace_directory(global_variables)

        for step in task.steps:
            host = None
            if step.host_id:
                host = get_host(step.host_id)
            variables = {
                **variables,
                "step_id": step.step_id,
                "step": step,
                "host_id": step.host_id,
                "host": host,
                "error": False,
                "error_message": "",
            }
            plugin_found = False
            for plugin in step_plugins.plugins:
                if step.active == 0:
                    logging.info(
                        f"Step is not active. Skipping step, step_id: {step.step_id}, "
                        f"script: {plugin.name.lower()}"
                    )
                elif step.script.lower() == plugin.name.lower():
                    plugin_found = True
                    variables = run_step_process(
                        global_variables, variables, step, plugin
                    )
                    if variables["error"]:
                        logging.error(
                            f"Error in step {step.step_id}, '{plugin.name.lower()}', "
                            f"message: '{variables['error_message']}'."
                        )
                        error = True
                        break
            if not plugin_found:
                logging.error(f"Plugin script '{step.script.lower()}' not found.")
                error = True
                break
            if error:
                break

        if not error or (error and not workspace_directory_files(global_variables)):
            delete_workspace_directory(global_variables)

        if error:
            logging.error(
                f"Error in task '{task.name}', id: {task.task_id}, "
                f"task_run_id: {workspace_id} halted."
            )
            add_task_log_entry(workspace_id, task.task_id, "error")
        else:
            logging.info(
                f"Task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id} completed."
            )
            add_task_log_entry(workspace_id, task.task_id, "success")

        logging.info(
            f"--- Exiting task '{task.name}', id: {task.task_id}, task_run_id: {workspace_id}, "
            f"thread {threading.get_native_id()}."
        )

    else:
        logging.error(f"Task id: {task.task_id}, not found.")


def run_step_process(global_variables, variables, step, plugin):
    """Run plugin for step in task."""
    add_step_log_entry(
        global_variables["workspace_id"],
        global_variables["task_id"],
        step.step_id,
        "running",
    )

    logging.debug(
        f"--- Running step '{plugin.name.lower()}', "
        f"input arguments={step.arguments}, {variables=}."
    )
    try:
        tmp = plugin(step.arguments, {**variables, **global_variables})
        tmp.process()
        variables = tmp.variables
    except Exception as exc:
        variables["error"] = True
        variables["error_message"] = exc

    add_step_log_entry(
        global_variables["workspace_id"],
        global_variables["task_id"],
        step.step_id,
        "error" if variables["error"] else "success",
    )
    logging.debug(f"--- Step '{plugin.name.lower()}' done, output {variables=}.")

    return variables


def workspace_directory_files(global_variables) -> list:
    """List all files in workspace directory."""
    files = os.listdir(global_variables["workspace_directory"])
    return files


def delete_workspace_directory(global_variables):
    """Delete the workspace directory."""
    shutil.rmtree(global_variables["workspace_directory"])
    logging.info(
        f"Deleted workspace directory '{global_variables['workspace_directory']}'."
    )


def create_workspace_directory(global_variables):
    """Create the workspace directory."""
    os.mkdir(global_variables["workspace_directory"])
    logging.info(
        f"Created workspace directory '{global_variables['workspace_directory']}'."
    )


def run_task_threaded(task: int):
    """Run task in thread."""
    new_thread = threading.Thread(target=run_task, args=(task,))
    new_thread.start()


@router.get("/status")
async def get_status():
    """Get tasks status."""
    return_data = []
    with SessionLocal() as db:
        for status in ("success", "error", "running", "no_files"):
            if status == "success":
                tmp = (
                    db.query(TaskLog.status, func.count(TaskLog.joblog_id))
                    .join(FileLog, FileLog.task_run_id == TaskLog.task_run_id)
                    .where(TaskLog.status == status)
                    .group_by(TaskLog.status)
                    .one_or_none()
                )
            elif status == "no_files":
                tmp = (
                    db.query(TaskLog.status, func.count(TaskLog.joblog_id))
                    .join(
                        FileLog,
                        FileLog.task_run_id == TaskLog.task_run_id,
                        isouter=True,
                    )
                    .where(
                        and_(
                            TaskLog.status == "success",
                            FileLog.filelog_id.is_(None),
                        )
                    )
                    .group_by(TaskLog.status)
                    .one_or_none()
                )
            else:
                tmp = (
                    db.query(TaskLog.status, func.count(TaskLog.joblog_id))
                    .where(TaskLog.status == status)
                    .group_by(TaskLog.status)
                    .one_or_none()
                )
            if tmp:
                return_data.append({"status": status, "count": tmp[1]})
            else:
                return_data.append({"status": status, "count": 0})
    return return_data


@router.get("/{task_id}")
async def get_task(task_id: int):
    """Get a task."""
    with SessionLocal() as db:
        db_task = (
            db.query(models.Task).filter(models.Task.task_id == task_id).one_or_none()
        )
        if not db_task:
            raise HTTPException(status_code=404, detail="task not found")
        db_task.schedules = await get_task_schedules(db_task.task_id)
        db_task.steps = await get_task_steps(db_task.task_id)
        return db_task


@router.get("/active")
async def get_active_tasks():
    """Get all active tasks."""
    with SessionLocal() as db:
        result = db.query(models.Task).filter(models.Task.active == 1).all()
        for row in result:
            row.schedules = await get_task_schedules(row.task_id)
            row.steps = await get_task_steps(row.task_id)
        return result


@router.get("")
async def get_tasks():
    """Get all tasks."""
    with SessionLocal() as db:
        result = db.query(models.Task).all()
        for row in result:
            row.schedules = await get_task_schedules(row.task_id)
            row.steps = await get_task_steps(row.task_id)
        return result


@router.post("", status_code=201)
async def add_task(task: shemas.AddTask):
    """Add a task."""
    with SessionLocal() as db:
        db_task = Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task


@router.put("/{task_id}")
async def update_task(task_id: int, task: shemas.AddTask):
    """Update a task."""
    with SessionLocal() as db:
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
    with SessionLocal() as db:
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
    with SessionLocal() as db:
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
    with SessionLocal() as db:
        db_task = (
            db.query(models.Schedule).filter(models.Schedule.task_id == task_id).all()
        )
        return db_task


@router.delete("/{task_id}/schedules/{schedule_id}", status_code=204)
async def delete_schedule(task_id: int, schedule_id: int):
    """Delete a schedule."""
    with SessionLocal() as db:
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
    run_task_threaded(db_task.task_id)
    return None
