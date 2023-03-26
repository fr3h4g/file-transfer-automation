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

from filetransferautomation import tasks
from filetransferautomation.common import compare_filter
from filetransferautomation.database_init import create_database

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

app = FastAPI()

scheduler = Scheduler()


app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


def local_directory_transfer(
    task: tasks.Task, step: tasks.Step, task_directory: str
) -> list:
    """Get and Send files from and to local directory in a task."""
    files_found = []

    if not step.directory:
        logging.error("Local directory is not set.")
        return files_found
    if not step.file_mask:
        logging.error("No file_mask set, use *.* for all files.")
        return files_found

    if step.step_type == "source":
        from_dir = step.directory
        to_dir = task_directory
    else:
        from_dir = task_directory
        to_dir = step.directory

    logging.info(f"Checking for files '{step.file_mask}' in directory '{from_dir}'.")

    files = os.listdir(from_dir)

    for filename in files:
        if compare_filter(filename, step.file_mask):
            files_found.append(filename)

    logging.info(f"{len(files_found)} files matched of {len(files)} files found.")

    files_sent = []
    for filename in files_found:
        if compare_filter(filename, step.file_mask):
            os.rename(
                os.path.join(from_dir, filename),
                os.path.join(from_dir, filename) + ".processing",
            )
            with open(
                os.path.join(from_dir, filename) + ".processing", "rb"
            ) as file_bytes:
                file_data = file_bytes.read()

            with open(os.path.join(to_dir, filename), "wb") as f_byte:
                f_byte.write(file_data)

            os.remove(os.path.join(from_dir, filename) + ".processing")

            files_sent.append(filename)

    if step.step_type == "source":
        logging.info(f"{len(files_sent)} files downloaded from {from_dir}.")
    else:
        logging.info(f"{len(files_sent)} files sent to {to_dir}.")

    return files_found


def run_task(task: tasks.Task):
    """Run task."""
    task_id = str(uuid.uuid4())
    logging.info(
        f"--- Running task '{task.name}', id: {task.id}, task_id: {task_id}, thread {threading.get_native_id()}."
    )
    task_directory = "./work/" + task_id + "/"
    os.mkdir(task_directory)
    found_files = []
    for step in task.steps:
        if step.step_type == "source" and step.type == "local_directory":
            found_files = local_directory_transfer(task, step, task_directory)
    if found_files:
        for step in task.steps:
            if step.step_type == "process":
                pass
        for step in task.steps:
            if step.step_type == "destination" and step.type == "local_directory":
                local_directory_transfer(task, step, task_directory)
    else:
        logging.info(f"Found no files on '{task.name}'.")
        logging.info(f"No files were retrieved.")
    os.rmdir(task_directory)
    logging.info(f"Task '{task.name}', id: {task.id}, task_id: {task_id} completed.")
    logging.info(
        f"--- Exiting task '{task.name}', id: {task.id}, task_id: {task_id}, thread {threading.get_native_id()}."
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

    logging.info("Creating database.")
    create_database()

    logging.info("Loading tasks.")
    tasks_data = tasks.load_tasks()
    logging.info(f"{len(tasks_data)} tasks loaded.")
    for task in tasks_data:
        if task.active:
            for schedule in task.schedules:
                scheduler.cron(str(schedule.cron)).do_function(run_task_threaded, task)
                run_task_threaded(task)

    asyncio.ensure_future(main())


if __name__ == "__main__":
    uvicorn.run(
        "filetransferautomation.__main__:app", host="0.0.0.0", port=8080, reload=True
    )
