"""Start File Transfer Automation."""
from __future__ import annotations

import uuid
import logging
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from scheduleplus.scheduler import Scheduler

from filetransferautomation import tasks


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

app = FastAPI()

scheduler = Scheduler()


app.include_router(
    tasks.router,
    prefix="/api/v1/tasks",
    tags=["tasks"],
)


def run_task(task: tasks.Task):
    task_id = str(uuid.uuid4())
    logging.info(f"Running task {task.name}, id: {task.id}, task_id: {task_id}")
    # create temp directory for task, uuid
    directory = "./_work/" + task_id + "/"
    for step in task.steps:
        if step.step_type == "source":
            print("running get files from source")
    for step in task.steps:
        if step.step_type == "process":
            print("running processing on files")
    for step in task.steps:
        if step.step_type == "destination":
            print("running send files to destination")
    # clean up temp directory


async def main():  # pragma: no cover
    while True:
        await asyncio.to_thread(scheduler.run_function_jobs)
        await asyncio.sleep(1)


@app.on_event("startup")
def startup():  # pragma: no cover
    logging.info("Loading tasks.")
    tasks_data = tasks.load_tasks()
    for task in tasks_data:
        if task.active:
            for schedule in task.schedules:
                scheduler.cron(str(schedule.cron)).do_function(run_task, task)
    logging.info(f"{len(tasks_data)} tasks loaded.")
    asyncio.ensure_future(main())
    scheduler.list_jobs()


if __name__ == "__main__":
    uvicorn.run(
        "filetransferautomation.__main__:app", host="0.0.0.0", port=8000, reload=True
    )
