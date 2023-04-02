"""Start File Transfer Automation."""
from __future__ import annotations
import argparse

import asyncio
import logging
import os
import sys

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


async def run_schedules() -> None:
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
                        tasks.run_task_threaded, task
                    )
                if settings.DEV_MODE:
                    tasks.run_task_threaded(task)

    asyncio.ensure_future(run_schedules())


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="File Transfer Automation: Managed File Transfers made easy.",
    )

    parser.add_argument(
        "-p",
        "--port",
        help="Port for REST api to listen on, default 8080",
        default=8080,
    )

    arguments = parser.parse_args()

    return arguments


def main():
    args = get_arguments()

    print(args)

    reload = False
    if settings.DEV_MODE:
        reload = True

    uvicorn.run(
        "filetransferautomation.__main__:app",
        host="0.0.0.0",
        port=args.port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
