"""Models."""
from __future__ import annotations

from typing import Literal

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Schedule(Base):
    """Table schedule model."""

    __tablename__ = "schedules"

    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"))
    cron: Mapped[str] = mapped_column(String)

    def __repr__(self):
        """Table repr."""
        return f"Schedule({self.schedule_id!r}, {self.task_id!r}, {self.cron!r})"


class Task(Base):
    """Table tasks model."""

    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    active: Mapped[int] = mapped_column(Integer)

    schedules: Mapped[list[Schedule]] = relationship()
    steps: Mapped[list[Step]] = relationship()

    def __repr__(self):
        """Table repr."""
        return f"Task(steps={self.steps!r}, schedules={self.schedules!r}"


class Step(Base):
    """Table steps model."""

    __tablename__ = "steps"

    step_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"))
    step_type: Mapped[
        Literal["source"] | Literal["process"] | Literal["destination"]
    ] = mapped_column(String)

    # directory: Mapped[str | None] = mapped_column(String, default=None)
    # type: Mapped[
    #     Literal["local_directory"] | Literal["rename"] | Literal["unc_share"] | None
    # ] = mapped_column(String, default=None)
    file_mask: Mapped[str | None] = mapped_column(String, default=None)
    filename: Mapped[str | None] = mapped_column(String, default=None)
    # username: Mapped[str | None] = mapped_column(String, default=None)
    # password: Mapped[str | None] = mapped_column(String, default=None)
    # share: Mapped[str | None] = mapped_column(String, default=None)
    run_per_file: Mapped[bool | None] = mapped_column(Boolean, default=None)
    name: Mapped[str | None] = mapped_column(String, default=None)
    max_file_count: Mapped[int | None] = mapped_column(Integer, default=None)

    host_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("hosts.host_id"), default=None
    )
    host: Mapped[Host] = relationship(lazy=False)

    process_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("processes.process_id"), default=None
    )
    process: Mapped[Process | None] = relationship()

    def __repr__(self):
        """Table repr."""
        return f"Step({self.step_id}, ...)"


class Process(Base):
    """Table processes model."""

    __tablename__ = "processes"

    process_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str | None] = mapped_column(String, default=None)


class Host(Base):
    """Table hosts model."""

    __tablename__ = "hosts"

    host_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    type: Mapped[Literal["local_directory"] | Literal["unc_share"]] = mapped_column(
        String, default=None
    )
    directory: Mapped[str | None] = mapped_column(String, default=None)
    share: Mapped[str | None] = mapped_column(String, default=None)
    username: Mapped[str | None] = mapped_column(String, default=None)
    password: Mapped[str | None] = mapped_column(String, default=None)
    description: Mapped[str | None] = mapped_column(String, default=None)
