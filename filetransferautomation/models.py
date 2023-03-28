"""Models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import uuid


@dataclass
class Task:
    """Task."""

    task_id: int
    name: str
    schedules: list[Schedule]
    steps: list[Step]
    description: str
    active: int


@dataclass
class Step:
    """Task Step."""

    step_id: int
    task_id: int
    step_type: Literal["source"] | Literal["process"] | Literal["destination"]
    host_id: int | None = None
    directory: str | None = None
    type: Literal["local_directory"] | Literal["rename"] | Literal[
        "unc_share"
    ] | None = None
    file_mask: str | None = None
    filename: str | None = None
    username: str | None = None
    password: str | None = None
    share: str | None = None
    run_per_file: bool | None = None
    name: str | None = None


@dataclass
class Schedule:
    """Schedule dataclass."""

    schedule_id: int
    task_id: int
    cron: str


@dataclass
class Host:
    """Host dataclass."""

    name: str
    type: Literal["local_directory"] | Literal["unc_share"]
    host_id: int | None = None
    directory: str | None = None
    share: str | None = None
    username: str | None = None
    password: str | None = None
    description: str | None = None


@dataclass
class Folder:
    """Folder dataclass."""

    folder_id: int
    name: str


@dataclass
class File:
    """File dataclass."""

    name: str
    file_id: str = str(uuid.uuid4())
