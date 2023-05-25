"""Models."""
from __future__ import annotations

import datetime
from typing import Literal

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class FileLog(Base):
    """Table file log model."""

    __tablename__ = "file_log"

    filelog_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_run_id: Mapped[str] = mapped_column(String(50))
    task_id: Mapped[int] = mapped_column(Integer)
    step_id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    file_name: Mapped[str] = mapped_column(String(255))
    size: Mapped[int | None] = mapped_column(BigInteger, default=None)
    status: Mapped[str] = mapped_column(String(30))
    duration_sec: Mapped[float | None] = mapped_column(Float, default=None)
    bytes_per_sec: Mapped[float | None] = mapped_column(BigInteger, default=None)


class TaskLog(Base):
    """Table task log model."""

    __tablename__ = "task_log"

    joblog_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_id: Mapped[int] = mapped_column(Integer)
    task_run_id: Mapped[str] = mapped_column(String(50))
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )
    status: Mapped[
        Literal["running"] | Literal["error"] | Literal["success"]
    ] = mapped_column(String(30))
    duration_sec: Mapped[float | None] = mapped_column(Float, default=None)


class StepLog(Base):
    """Table task log model."""

    __tablename__ = "step_log"

    steplog_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_id: Mapped[int] = mapped_column(Integer)
    task_run_id: Mapped[str] = mapped_column(String(50))
    step_id: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )
    status: Mapped[
        Literal["running"] | Literal["error"] | Literal["success"]
    ] = mapped_column(String(30))
    duration_sec: Mapped[float | None] = mapped_column(Float, default=None)


class Schedule(Base):
    """Table schedule model."""

    __tablename__ = "schedules"

    schedule_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_id: Mapped[int] = mapped_column(Integer)
    cron: Mapped[str] = mapped_column(String(255))

    scheduler_job_id: Mapped[int | None] = mapped_column(Integer, default=None)


class Task(Base):
    """Table tasks model."""

    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    active: Mapped[int] = mapped_column(Integer)


class Step(Base):
    """Table steps model."""

    __tablename__ = "steps"

    step_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    sort_order: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[int] = mapped_column(Integer)
    host_id: Mapped[int | None] = mapped_column(Integer, default=None)
    script: Mapped[str | None] = mapped_column(String(100), default=None)
    arguments: Mapped[Text | None] = mapped_column(Text, default=None)
    active: Mapped[int] = mapped_column(Integer, default=1)


# class Process(Base):
#     """Table processes model."""

#     __tablename__ = "processes"

#     process_id: Mapped[int] = mapped_column(
#         Integer, primary_key=True, index=True, unique=True, autoincrement=True
#     )
#     name: Mapped[str | None] = mapped_column(String(100), default=None)
#     script_file: Mapped[str | None] = mapped_column(String(100), default=None)
#     per_file: Mapped[int] = mapped_column(Integer, default=0)


class Host(Base):
    """Table hosts model."""

    __tablename__ = "hosts"

    host_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[Literal["local_directory"] | Literal["unc_share"]] = mapped_column(
        String(50), default=None
    )
    directory: Mapped[str | None] = mapped_column(String(255), default=None)
    share: Mapped[str | None] = mapped_column(String(255), default=None)
    host: Mapped[str | None] = mapped_column(String(100), default=None)
    port: Mapped[int | None] = mapped_column(Integer, default=None)
    username: Mapped[str | None] = mapped_column(String(100), default=None)
    password: Mapped[str | None] = mapped_column(String(100), default=None)
    description: Mapped[str | None] = mapped_column(String(255), default=None)


class Folder(Base):
    """Table hosts model."""

    __tablename__ = "folders"

    folder_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255), default=None)
