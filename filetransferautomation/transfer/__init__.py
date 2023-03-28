"""Transfer."""
from __future__ import annotations

from typing import Literal

from filetransferautomation import steps, tasks
from filetransferautomation.transfer.protocols.local_directory import LocalDirectory


class Transfer:
    """Transfer to/from host with used protocol."""

    _transfer_protocol = None

    def __init__(
        self,
        transfer_type: Literal["local_directory"],
        direction: Literal["download"] | Literal["upload"],
        task: tasks.Task,
        step: steps.Step,
        work_directory: str,
    ):
        """Init transfer and load protocol."""
        if transfer_type == "local_directory":
            self._transfer_protocol = LocalDirectory(
                direction=direction, task=task, step=step, work_directory=work_directory
            )

    def run(self) -> list[str]:
        """Run transfer with loaded protocol."""
        if self._transfer_protocol:
            return self._transfer_protocol.run()
        return []
