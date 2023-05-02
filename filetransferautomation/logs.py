"""Logs."""
import datetime
from typing import Literal

from fastapi import APIRouter

from filetransferautomation.database import SessionLocal
from filetransferautomation.models import FileLog, StepLog, TaskLog
from filetransferautomation.shemas import File

from sqlalchemy import func

router = APIRouter()

# class TaskLog(BaseModel):
#     joblog_id: int
#     task_id: int
#     task_run_id: str
#     start_time: datetime.datetime
#     end_time: datetime.datetime
#     status: Literal["running"] | Literal["error"] | Literal["done"]
#     duration_sec: int


# class FileLog(BaseModel):
#     filelog_id: int
#     job_id: str
#     task_id: int
#     step_id: int
#     timestamp: datetime.datetime
#     file_id: str
#     file_name: str
#     size: int
#     status: str
#     duration_sec: int
#     transfer_speed: str


# class ProcessLog(BaseModel):
#     proclog_id: int
#     job_id: str
#     task_id: int
#     step_id: int
#     name: str
#     start_time: datetime.datetime
#     end_time: datetime.datetime
#     status: str
#     std_out: str
#     duration_sec: int


def add_file_log_entry(
    task_run_id: str,
    task_id: int,
    step_id: int,
    filename: File,
    status: str,
    filesize: int | None = None,
    duration_sec: float | None = None,
    bytes_per_sec: float | None = None,
):
    """Add file log entry."""
    timestamp = datetime.datetime.now()
    with SessionLocal() as db:
        db_file_log = FileLog(
            task_run_id=task_run_id,
            task_id=task_id,
            step_id=step_id,
            status=status,
            file_name=filename,
            size=filesize,
            timestamp=timestamp,
        )
        if filesize:
            db_file_log.size = filesize
        if duration_sec:
            db_file_log.duration_sec = duration_sec
        if bytes_per_sec:
            db_file_log.bytes_per_sec = bytes_per_sec
        db.add(db_file_log)
        db.commit()


def add_task_log_entry(
    task_run_id: str,
    task_id: int,
    status: Literal["running"] | Literal["error"] | Literal["success"],
):
    """Add task log entry."""
    timestamp = datetime.datetime.now()

    with SessionLocal() as db:
        db_task_log = (
            db.query(TaskLog).filter(TaskLog.task_run_id == task_run_id).one_or_none()
        )
        if db_task_log:
            db_task_log.end_time = timestamp
            db_task_log.status = status
            db_task_log.duration_sec = (
                timestamp - db_task_log.start_time
            ).total_seconds()
            db.commit()
            return None
        db_task_log = TaskLog(
            task_run_id=task_run_id,
            task_id=task_id,
            status=status,
            start_time=timestamp,
        )
        db.add(db_task_log)
        db.commit()


def add_step_log_entry(
    task_run_id: str,
    task_id: int,
    step_id: int,
    status: Literal["running"] | Literal["error"] | Literal["success"],
):
    """Add s log entry."""
    timestamp = datetime.datetime.now()

    with SessionLocal() as db:
        db_task_log = (
            db.query(StepLog)
            .filter(StepLog.task_run_id == task_run_id, StepLog.step_id == step_id)
            .one_or_none()
        )
        if db_task_log:
            db_task_log.end_time = timestamp
            db_task_log.status = status
            db_task_log.duration_sec = (
                timestamp - db_task_log.start_time
            ).total_seconds()
            db.commit()
            return None
        db_task_log = StepLog(
            task_run_id=task_run_id,
            task_id=task_id,
            step_id=step_id,
            status=status,
            start_time=timestamp,
        )
        db.add(db_task_log)
        db.commit()


@router.get("/files")
def get_files_log(limit: int = 100):
    """Get all file log entrys."""
    with SessionLocal() as db:
        tmp = (
            db.query(func.max(FileLog.filelog_id))
            .group_by(
                FileLog.task_run_id, FileLog.task_id, FileLog.step_id, FileLog.file_name
            )
            .order_by(FileLog.filelog_id.desc())
            .limit(limit=limit)
            .all()
        )
        latest_file_ids = []
        for row in tmp:
            latest_file_ids.append(row[0])
        db_file_log = (
            db.query(FileLog)
            .where(FileLog.filelog_id.in_(latest_file_ids))
            .order_by(FileLog.filelog_id.desc())
            .all()
        )
        return db_file_log


@router.get("/tasks")
def get_tasks_log(limit: int = 30):
    """Get all tasks log entrys."""
    with SessionLocal() as db:
        db_task_log = (
            db.query(TaskLog)
            .order_by(TaskLog.joblog_id.desc())
            .limit(limit=limit)
            .all()
        )
        return db_task_log


@router.get("/tasks/{task_run_id}")
def get_task_log(task_run_id: str):
    """Get a task log entry."""
    with SessionLocal() as db:
        db_task_log = (
            db.query(TaskLog).filter(TaskLog.task_run_id == task_run_id).one_or_none()
        )
        if db_task_log:
            db_files_download_log = (
                db.query(FileLog)
                .filter(
                    FileLog.task_run_id == task_run_id,
                    FileLog.status == "downloaded",
                )
                .all()
            )
            db_files_upload_log = (
                db.query(FileLog)
                .filter(
                    FileLog.task_run_id == task_run_id,
                    FileLog.status == "uploaded",
                )
                .all()
            )
            db_task_log.files_downloaded = db_files_download_log
            db_task_log.files_uploaded = db_files_upload_log
        return db_task_log
