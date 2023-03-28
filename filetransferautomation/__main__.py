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

from filetransferautomation import folders, hosts, schedules, settings, steps, tasks
from filetransferautomation.common import compare_filter
from filetransferautomation.transfer import Transfer

# from filetransferautomation.database_init import create_database

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
    folders.router,
    prefix="/api/v1/folders",
    tags=["folders"],
)


def rename_process(task: tasks.Task, step: steps.Step, work_directory: str):
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


def run_task(task: tasks.Task):
    """Run task."""
    task_id = str(uuid.uuid4())
    logging.info(
        f"--- Running task '{task.name}', id: {task.task_id}, task_id: {task_id}, thread {threading.get_native_id()}."
    )
    work_directory = os.path.join(settings.WORK_DIR, task_id)
    os.mkdir(work_directory)
    downloaded_files = []
    for step in task.steps:
        if step.step_type == "source" and step.type:
            # found_files = local_directory_transfer(task, step, work_directory)
            transfer = Transfer(step.type, "download", task, step, work_directory)
            downloaded_files = transfer.run()
    if downloaded_files:
        for step in task.steps:
            if step.step_type == "process":
                if step.type == "rename":
                    rename_process(task, step, work_directory)
                elif step.type == "script":
                    pass
        for step in task.steps:
            if step.step_type == "destination" and step.type:
                transfer = Transfer(step.type, "upload", task, step, work_directory)
                transfer.run()
    os.rmdir(work_directory)
    logging.info(
        f"Task '{task.name}', id: {task.task_id}, task_id: {task_id} completed."
    )
    logging.info(
        f"--- Exiting task '{task.name}', id: {task.task_id}, task_id: {task_id}, thread {threading.get_native_id()}."
    )


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

    # logging.info("Creating database.")
    # create_database()

    logging.info("Loading hosts.")
    hosts_data = hosts.load_hosts()
    logging.info(f"{len(hosts_data)} hosts loaded.")

    logging.info("Loading schedules.")
    schedules_data = schedules.load_schedules()
    logging.info(f"{len(schedules_data)} schedules loaded.")

    logging.info("Loading steps.")
    steps_data = steps.load_steps()
    logging.info(f"{len(steps_data)} steps loaded.")

    logging.info("Loading folders.")
    folders_data = folders.load_folders()
    logging.info(f"{len(folders_data)} folders loaded.")

    logging.info("Loading tasks.")
    tasks_data = tasks.load_tasks()
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
