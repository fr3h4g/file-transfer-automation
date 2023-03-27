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

# from filetransferautomation.database_init import create_database

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

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


def local_directory_transfer(
    task: tasks.Task, step: tasks.Step, work_directory: str
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
        to_dir = work_directory
        direction = "download"
    else:
        from_dir = work_directory
        to_dir = step.directory
        direction = "upload"

    temp_ext = f".{direction}"

    logging.info(f"Checking for files '{step.file_mask}' in directory '{from_dir}'.")

    files = os.listdir(from_dir)

    for filename in files:
        if compare_filter(filename, step.file_mask):
            files_found.append(filename)

    logging.info(f"{len(files_found)} files matched of {len(files)} files found.")

    files_sent = []
    for filename in files_found:
        os.rename(
            os.path.join(from_dir, filename),
            os.path.join(from_dir, filename) + temp_ext,
        )
        with open(os.path.join(from_dir, filename) + temp_ext, "rb") as file_bytes:
            file_data = file_bytes.read()

        with open(os.path.join(to_dir, filename), "wb") as f_byte:
            f_byte.write(file_data)

        os.remove(os.path.join(from_dir, filename) + temp_ext)

        files_sent.append(filename)

    if direction == "download":
        logging.info(f"{len(files_sent)} files downloaded from {from_dir}.")
    else:
        logging.info(f"{len(files_sent)} files uploaded to {to_dir}.")

    return files_found


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
    found_files = []
    for step in task.steps:
        if step.step_type == "source" and step.type == "local_directory":
            found_files = local_directory_transfer(task, step, work_directory)
    if found_files:
        for step in task.steps:
            if step.step_type == "process":
                if step.type == "rename":
                    rename_process(task, step, work_directory)
                elif step.type == "script":
                    pass
        for step in task.steps:
            if step.step_type == "destination" and step.type == "local_directory":
                local_directory_transfer(task, step, work_directory)
    else:
        logging.info(f"Found no files on '{task.name}'.")
        logging.info("No files were retrieved.")
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
                scheduler.cron(str(schedule.cron)).do_function(run_task_threaded, task)
                run_task_threaded(task)

    asyncio.ensure_future(main())


if __name__ == "__main__":
    uvicorn.run(
        "filetransferautomation.__main__:app", host="0.0.0.0", port=8080, reload=True
    )
