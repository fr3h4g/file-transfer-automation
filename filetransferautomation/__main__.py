"""Start File Transfer Automation."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import uuid

from fastapi import FastAPI
from scheduleplus.scheduler import Scheduler
import uvicorn

from filetransferautomation import (
    folders,
    hosts,
    logs,
    schedules,
    settings,
    steps,
    tasks,
)
from filetransferautomation.common import compare_filter
from filetransferautomation.logs import add_task_log_entry
from filetransferautomation.transfer import Transfer

from . import models
from .database import engine

if not settings.DEV_MODE:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
if settings.DEV_MODE:
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)


app = FastAPI()

scheduler = Scheduler()


app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["tasks"],
)

app.include_router(
    hosts.router,
    prefix="/api/v1/hosts",
    tags=["hosts"],
)

app.include_router(
    steps.router,
    prefix="/api/v1/steps",
    tags=["steps"],
)

app.include_router(
    schedules.router,
    prefix="/api/v1/schedules",
    tags=["schedules"],
)

app.include_router(
    folders.router,
    prefix="/api/v1/folders",
    tags=["folders"],
)

app.include_router(
    logs.router,
    prefix="/api/v1/logs",
    tags=["logs"],
)


def rename_process(task: tasks.Task, step: models.Step, work_directory: str):
    """Rename a file."""
    files_renamed = []

    if not step.filename:
        logging.error("Step filename is not set.")
        return files_renamed

    if not step.file_mask:
        logging.error("No file_mask set, use *.* for all files.")
        return files_renamed

    from_dir = work_directory

    files = os.listdir(from_dir)
    for filename in files:
        if compare_filter(filename, step.file_mask):
            logging.info(f"Renaming file '{filename}' to '{step.filename}'.")
            os.rename(
                os.path.join(from_dir, filename), os.path.join(from_dir, step.filename)
            )
            files_renamed.append(filename)


def run_task(task: models.Task):
    """Run task."""
    task_run_id = str(uuid.uuid4())
    logging.info(
        f"--- Running task '{task.name}', id: {task.task_id}, task_run_id: {task_run_id}, thread {threading.get_native_id()}."
    )
    add_task_log_entry(task_run_id, task.task_id, "running")
    work_directory = os.path.join(settings.WORK_DIR, task_run_id)
    os.mkdir(work_directory)
    downloaded_files = []
    for step in task.steps:
        if step.host and step.step_type == "source" and step.host.type:
            # found_files = local_directory_transfer(task, step, work_directory)
            transfer = Transfer(
                step.host.type, "download", task, step, work_directory, task_run_id
            )
            downloaded_files = transfer.run()
    if downloaded_files:
        for step in task.steps:
            if step.step_type == "process":
                if step.type == "rename":
                    rename_process(task, step, work_directory)
                elif step.type == "script":
                    pass
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
        f"--- Exiting task '{task.name}', id: {task.task_id}, task_run_id: {task_run_id}, thread {threading.get_native_id()}."
    )
    add_task_log_entry(task_run_id, task.task_id, "done")


def run_task_threaded(task: tasks.Task):
    """Run task in thread."""
    new_thread = threading.Thread(target=run_task, args=(task,))
    new_thread.start()


async def main() -> None:
    """Run all schedules."""
    while True:
        await asyncio.to_thread(scheduler.run_function_jobs)
        await asyncio.sleep(1)


@app.on_event("startup")
def startup():
    """Start File Transfer Automation."""

    models.Base.metadata.create_all(bind=engine)

    logging.info("Loading folders.")
    folders_data = folders.load_folders()
    logging.info(f"{len(folders_data)} folders loaded.")

    logging.info("Loading tasks.")
    tasks_data = tasks.get_active_tasks()
    logging.info(f"{len(tasks_data)} tasks loaded.")
    for task in tasks_data:
        if task.active:
            for schedule in task.schedules:
                if not settings.DEV_MODE:
                    scheduler.cron(str(schedule.cron)).do_function(
                        run_task_threaded, task
                    )
                if settings.DEV_MODE:
                    run_task_threaded(task)

    asyncio.ensure_future(main())


if __name__ == "__main__":
    uvicorn.run(
        "filetransferautomation.__main__:app", host="0.0.0.0", port=8080, reload=True
    )
