"""Start File Transfer Automation."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from fastapi import FastAPI
import uvicorn

from filetransferautomation import (
    folders,
    hosts,
    jobs,
    logs,
    schedules,
    settings,
    steps,
    tasks,
)
from filetransferautomation.jobs import load_jobs, run_schedules

from . import models
from .database import engine

if not settings.DEV_MODE:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
if settings.DEV_MODE:
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logging.getLogger("smbprotocol").setLevel(logging.DEBUG)


app = FastAPI()


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

app.include_router(
    jobs.router,
    prefix="/api/v1/jobs",
    tags=["jobs"],
)


def setup_std_folders():
    """Make std folders."""
    if not os.path.exists(settings.FOLDERS_DIR):
        os.makedirs(settings.FOLDERS_DIR)
    if not os.path.exists(settings.WORK_DIR):
        os.makedirs(settings.WORK_DIR)


@app.on_event("startup")
async def startup():
    """Start File Transfer Automation."""

    models.Base.metadata.create_all(bind=engine)

    setup_std_folders()

    logging.info("Loading folders.")
    folders_data = folders.load_folders()
    logging.info(f"{len(folders_data)} folders loaded.")

    await load_jobs()

    asyncio.ensure_future(run_schedules())


def get_arguments() -> argparse.Namespace:
    """Get CLI arguments."""
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
    """Startup."""
    args = get_arguments()

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
