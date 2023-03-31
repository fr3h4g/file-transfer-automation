"""Logs."""
import datetime
from typing import Literal

from fastapi import APIRouter

from filetransferautomation.database import SessionLocal
from filetransferautomation.models import FileLog, TaskLog
from filetransferautomation.shemas import File

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
    file: File,
    status: str,
):
    """Add file log entry."""
    timestamp = datetime.datetime.now()
    db = SessionLocal()
    db_file_log = FileLog(
        task_run_id=task_run_id,
        task_id=task_id,
        step_id=step_id,
        status=status,
        file_id=file.file_id,
        file_name=file.name.removesuffix(".processing"),
        size=file.size,
        timestamp=timestamp,
    )
    if status in ("uploaded", "downloaded"):
        get_status = "uploading" if status == "uploaded" else "downloading"
        db_file_start = (
            db.query(FileLog)
            .filter(FileLog.file_id == file.file_id, FileLog.status == get_status)
            .one_or_none()
        )
        if db_file_start:
            db_file_log.duration_sec = (
                timestamp - db_file_start.timestamp
            ).total_seconds()
            if file.size:
                db_file_log.transfer_speed = (
                    str(round(file.size / db_file_log.duration_sec)) + " Bytes/sec"
                )
    db.add(db_file_log)
    db.commit()


def add_task_log_entry(
    task_run_id: str,
    task_id: int,
    status: Literal["running"] | Literal["error"] | Literal["done"],
):
    """Add task log entry."""
    timestamp = datetime.datetime.now()

    db = SessionLocal()
    db_task_log = (
        db.query(TaskLog).filter(TaskLog.task_run_id == task_run_id).one_or_none()
    )
    if db_task_log:
        db_task_log.end_time = timestamp
        db_task_log.status = status
        db_task_log.duration_sec = (timestamp - db_task_log.start_time).total_seconds()
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


@router.get("/files")
def get_files_log():
    """Get all file log entrys."""
    db = SessionLocal()
    db_file_log = db.query(FileLog).all()
    return db_file_log


@router.get("/tasks")
def get_tasks_log():
    """Get all tasks log entrys."""
    db = SessionLocal()
    db_task_log = db.query(TaskLog).all()
    return db_task_log


@router.get("/tasks/{task_run_id}")
def get_task_log(task_run_id: str):
    """Get a task log entry."""
    db = SessionLocal()
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
