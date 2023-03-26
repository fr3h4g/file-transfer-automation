"""Steps data."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from filetransferautomation.hosts import get_host


@dataclass
class Step:
    """Task Step."""

    step_id: int
    task_id: int
    step_type: Literal["source"] | Literal["process"] | Literal["destination"]
    host_id: int | None = None
    directory: str | None = None
    type: str | None = None
    file_mask: str | None = None
    filename: str | None = None
    username: str | None = None
    password: str | None = None
    share: str | None = None
    run_per_file: bool | None = None


STEPS: list[Step] = []


def load_steps() -> list[Step]:
    """Load steps from database."""
    global STEPS
    STEPS.append(
        Step(
            step_id=1,
            task_id=1,
            step_type="source",
            host_id=1,
            file_mask="*.txt",
        )
    )
    STEPS.append(
        Step(
            step_id=2,
            task_id=1,
            step_type="destination",
            host_id=2,
            file_mask="*.txt",
        )
    )
    STEPS.append(
        Step(
            step_id=3,
            task_id=1,
            step_type="process",
            type="rename",
            file_mask="cool.txt",
            filename="test.txt",
        )
    )
    return STEPS


def get_steps(task_id: int) -> list[Step]:
    """Get all steps for a task."""
    return_data = []
    for step in STEPS:
        if step.task_id == task_id and step.step_type == "source":
            step_dict = {**asdict(step), **asdict(get_host(step.host_id))}
            return_data.append(Step(**step_dict))
    for step in STEPS:
        if step.task_id == task_id and step.step_type == "process":
            return_data.append(Step(**asdict(step)))
    for step in STEPS:
        if step.task_id == task_id and step.step_type == "destination":
            step_dict = {**asdict(step), **asdict(get_host(step.host_id))}
            return_data.append(Step(**step_dict))
    return return_data
