"""Transfer."""
from __future__ import annotations

from typing import Literal

from filetransferautomation import steps, tasks
from filetransferautomation.shemas import File
from filetransferautomation.transfer.protocols.local_directory import LocalDirectory


class Transfer:
    """Transfer to/from host with used protocol."""

    _transfer_protocol = None

    def __init__(
        self,
        transfer_type: str,
        direction: Literal["download"] | Literal["upload"],
        task: tasks.Task,
        step: steps.Step,
        work_directory: str,
        task_run_id: str,
    ):
        """Init transfer and load protocol."""
        if transfer_type == "local_directory":
            self._transfer_protocol = LocalDirectory(
                direction=direction,
                task=task,
                step=step,
                work_directory=work_directory,
                task_run_id=task_run_id,
            )

    def run(self) -> list[File]:
        """Run transfer with loaded protocol."""
        if self._transfer_protocol:
            return self._transfer_protocol.run()
        return []
