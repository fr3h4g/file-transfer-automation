"""Steps data."""
from __future__ import annotations

from dataclasses import asdict

from filetransferautomation.hosts import get_host
from filetransferautomation.models import Step

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
        host = None
        if step.host_id:
            host = get_host(step.host_id)
        if host and step.task_id == task_id and step.step_type == "source":
            step_dict = {**asdict(step), **asdict(host)}
            return_data.append(Step(**step_dict))
    for step in STEPS:
        if step.task_id == task_id and step.step_type == "process":
            return_data.append(Step(**asdict(step)))
    for step in STEPS:
        host = None
        if step.host_id:
            host = get_host(step.host_id)
        if host and step.task_id == task_id and step.step_type == "destination":
            step_dict = {**asdict(step), **asdict(host)}
            return_data.append(Step(**step_dict))
    return return_data
