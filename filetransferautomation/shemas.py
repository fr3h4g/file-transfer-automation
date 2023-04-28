"""Schemas."""
from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Literal

from pydantic import BaseModel


@dataclass
class Folder:
    """Folder dataclass."""

    folder_id: int
    name: str
    description: str


@dataclass
class File:
    """File dataclass."""

    name: str
    file_id: str | None = None
    task_id: int | None = None
    size: int | None = None
    timestamp: datetime.datetime | None = None


class AddTask(BaseModel):
    """Add task model."""

    name: str
    description: str | None = ""
    active: int = 1


class AddHost(BaseModel):
    """Add host model."""

    name: str
    type: Literal["local_directory"] | Literal["unc_share"]
    directory: str | None = None
    share: str | None = None
    username: str | None = None
    password: str | None = None
    description: str | None = None


class AddStep(BaseModel):
    """Add steps model."""

    task_id: int
    step_type: Literal["source"] | Literal["process"] | Literal["destination"]
    file_mask: str | None = None
    filename: str | None = None
    run_per_file: bool | None = None
    name: str | None = None
    max_file_count: int | None = None
    host_id: int | None = None
    process_id: int | None = None


class AddSchedule(BaseModel):
    """Add schedule model."""

    task_id: int
    cron: str
