"""Scheduled jobs."""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter
from scheduleplus.scheduler import Scheduler

from filetransferautomation import schedules, tasks

router = APIRouter()

scheduler = Scheduler()


async def run_schedules() -> None:
    """Run all schedules."""
    while True:
        await asyncio.to_thread(scheduler.run_function_jobs)
        await asyncio.sleep(1)


async def load_jobs():
    """Load jobs in scheduler."""
    logging.info("Loading jobs.")
    tasks_data = await tasks.get_active_tasks()
    logging.info(f"{len(tasks_data)} jobs loaded.")
    for task in tasks_data:
        if task.active:
            for schedule in task.schedules:
                job = scheduler.cron(str(schedule.cron))
                if job._id:
                    await schedules.update_schedule_job_id(
                        schedule.schedule_id, job._id
                    )
                job.do_function(tasks.run_task_threaded, task)


@router.get("")
async def get_jobs():
    """Get all jobs."""
    return_data = []
    for job in scheduler._jobs:
        return_data.append(
            {
                "job_schedule_id": job.id(),
                "cron": job.cron_str(),
                "next_run": job.next_run(),
                "time_left": job.time_left(),
            }
        )
    return return_data


@router.get("/reload")
async def reload_jobs():
    """Reload jobs."""
    scheduler._next_job_id = 1
    scheduler._jobs = []
    await load_jobs()
    return_data = []
    for job in scheduler._jobs:
        return_data.append(
            {
                "job_schedule_id": job.id(),
                "cron": job.cron_str(),
                "next_run": job.next_run(),
                "time_left": job.time_left(),
            }
        )
    return return_data
