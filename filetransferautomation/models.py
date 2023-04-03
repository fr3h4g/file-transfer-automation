"""Models."""
from __future__ import annotations

import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class FileLog(Base):
    """Table file log model."""

    __tablename__ = "file_log"

    filelog_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_run_id: Mapped[str] = mapped_column(String(50))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"))
    step_id: Mapped[int] = mapped_column(Integer, ForeignKey("steps.step_id"))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now()
    )
    file_id: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30))
    duration_sec: Mapped[float | None] = mapped_column(Float, default=None)
    transfer_speed: Mapped[str | None] = mapped_column(String(50), default=None)


class TaskLog(Base):
    """Table task log model."""

    __tablename__ = "task_log"

    joblog_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"))
    task_run_id: Mapped[str] = mapped_column(String(50))
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
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"))
    cron: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        """Table repr."""
        return f"Schedule({self.schedule_id!r}, {self.task_id!r}, {self.cron!r})"


class Task(Base):
    """Table tasks model."""

    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    active: Mapped[int] = mapped_column(Integer)
    schedules: Mapped[list[Schedule]] = relationship(lazy="selectin")
    steps: Mapped[list[Step]] = relationship(lazy="selectin")

    def __repr__(self):
        """Table repr."""
        return f"Task(steps={self.steps!r}, schedules={self.schedules!r}"


class Step(Base):
    """Table steps model."""

    __tablename__ = "steps"

    step_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"))
    step_type: Mapped[
        Literal["source"] | Literal["process"] | Literal["destination"]
    ] = mapped_column(String(50))
    file_mask: Mapped[str | None] = mapped_column(String(255), default=None)
    filename: Mapped[str | None] = mapped_column(String(255), default=None)
    run_per_file: Mapped[bool | None] = mapped_column(Boolean, default=None)
    name: Mapped[str | None] = mapped_column(String(100), default=None)
    max_file_count: Mapped[int | None] = mapped_column(Integer, default=None)
    host_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hosts.host_id"), default=None
    )
    host: Mapped[Host] = relationship(lazy="selectin")
    process_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("processes.process_id"), default=None
    )
    process: Mapped[Process | None] = relationship(lazy="selectin")

    def __repr__(self):
        """Table repr."""
        return f"Step({self.step_id}, ...)"


class Process(Base):
    """Table processes model."""

    __tablename__ = "processes"

    process_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    name: Mapped[str | None] = mapped_column(String(100), default=None)
    script_file: Mapped[str | None] = mapped_column(String(100), default=None)
    per_file: Mapped[int] = mapped_column(Integer, default=0)


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
    username: Mapped[str | None] = mapped_column(String(100), default=None)
    password: Mapped[str | None] = mapped_column(String(100), default=None)
    description: Mapped[str | None] = mapped_column(String(255), default=None)
