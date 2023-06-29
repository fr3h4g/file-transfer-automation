"""Logs."""
import datetime
from typing import Literal

from fastapi import APIRouter
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import aliased

from filetransferautomation.database import SessionLocal
from filetransferautomation.human_bytes import HumanBytes
from filetransferautomation.models import FileLog, Host, Step, StepLog, Task, TaskLog
from filetransferautomation.shemas import File

router = APIRouter()


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
@router.get("/files/{task_run_id}")
def get_files_log(limit: int = 30, task_run_id: str = ""):
    """Get all file log entrys."""
    with SessionLocal() as db:
        tmp = (
            db.query(func.max(FileLog.filelog_id))
            .group_by(
                FileLog.task_run_id,
                FileLog.task_id,
                FileLog.step_id,
                FileLog.file_name,
            )
            .order_by(FileLog.filelog_id.desc())
            .limit(limit=limit)
            .all()
        )
        latest_file_ids = []
        for row in tmp:
            latest_file_ids.append(row[0])
        db_file_log = (
            db.query(FileLog, Task.name)
            .join(Task, Task.task_id == FileLog.task_id)
            .where(FileLog.filelog_id.in_(latest_file_ids))
        )
        if task_run_id:
            db_file_log = db_file_log.where(
                FileLog.task_run_id == task_run_id
            ).order_by(FileLog.filelog_id.asc())
        else:
            db_file_log = db_file_log.order_by(FileLog.filelog_id.desc())
        db_file_log = db_file_log.all()
        return_data = []
        for row in db_file_log:
            tmp = dict(row._mapping.items())
            tmp = {**tmp["FileLog"].__dict__, **tmp}
            del tmp["FileLog"]
            tmp["speed"] = ""
            if tmp["bytes_per_sec"]:
                tmp["speed"] = (
                    HumanBytes.format(float(tmp["bytes_per_sec"]), metric=True) + "/sec"
                )
            if tmp["size"]:
                tmp["size"] = HumanBytes.format(
                    float(tmp["size"]), metric=True, precision=3
                )
            tmp["duration"] = ""
            if tmp["duration_sec"]:
                tmp["duration"] = human_seconds(tmp["duration_sec"])
            del tmp["bytes_per_sec"]
            del tmp["duration_sec"]
            return_data.append(tmp)
        return return_data


def human_seconds(seconds: int) -> str:
    """Human readable seconds in format hours:minutes:seconds."""
    min, sec = divmod(seconds, 60)
    hr, min = divmod(min, 60)
    return f"{hr:.0f}h {min:.0f}m {sec:.0f}s"


@router.get("/steps")
@router.get("/steps/{task_run_id}")
def get_steps_log(limit: int = 30, task_run_id: str = ""):
    """Get all tasks log entrys."""
    with SessionLocal() as db:
        db_task_log = (
            db.query(
                StepLog.start_time,
                StepLog.end_time,
                StepLog.duration_sec,
                StepLog.status,
                Step.script,
                Host.name,
            )
            .join(Step, Step.step_id == StepLog.step_id)
            .join(Host, Host.host_id == Step.host_id)
        )

        if task_run_id:
            db_task_log = db_task_log.where(
                StepLog.task_run_id == task_run_id
            ).order_by(StepLog.steplog_id.asc())
        else:
            db_task_log = db_task_log.order_by(StepLog.steplog_id.desc())
        db_task_log = db_task_log.limit(limit=limit).all()
        return_data = []
        for row in db_task_log:
            tmp = dict(row._mapping.items())
            if "duration" in tmp and tmp["duration"]:
                tmp["duration"] = human_seconds(tmp["duration_sec"])
            del tmp["duration_sec"]
            return_data.append(tmp)
        return return_data


@router.get("/tasks")
def get_tasks_log(limit: int = 30, status: str = ""):
    """Get all tasks log entrys."""
    with SessionLocal() as db:
        filelog1 = aliased(FileLog)
        filelog2 = aliased(FileLog)
        db_task_log = (
            db.query(
                TaskLog.task_run_id,
                TaskLog.duration_sec,
                TaskLog.start_time,
                TaskLog.end_time,
                TaskLog.status,
                Task.name,
                func.count(filelog1.filelog_id.distinct()).label("downloaded_files"),
                func.count(filelog2.filelog_id.distinct()).label("uploaded_files"),
            )
            .join(Task, Task.task_id == TaskLog.task_id, isouter=True)
            .join(
                filelog1,
                and_(
                    filelog1.task_run_id == TaskLog.task_run_id,
                    filelog1.status == "downloaded",
                ),
                isouter=True,
            )
            .join(
                filelog2,
                and_(
                    filelog2.task_run_id == TaskLog.task_run_id,
                    or_(
                        filelog2.status == "uploaded",
                        filelog2.status == "mailed",
                    ),
                ),
                isouter=True,
            )
            .where(
                or_(filelog1.task_run_id.isnot(None), filelog2.task_run_id.isnot(None))
            )
            .order_by(TaskLog.joblog_id.desc())
            .group_by(TaskLog.task_run_id)
        )
        if status:
            db_task_log = db_task_log.where(TaskLog.status == status)
        db_task_log = db_task_log.limit(limit=limit).all()
        return_data = []
        for row in db_task_log:
            tmp = dict(row._mapping.items())
            tmp["duration"] = human_seconds(tmp["duration_sec"])
            del tmp["duration_sec"]
            return_data.append(tmp)
        return return_data
