from __future__ import annotations
import os

from typing import Literal

from filetransferautomation import steps, tasks
from .base_protocol import BaseProtocol


class LocalDirectory(BaseProtocol):
    def _connect(self):
        if self._direction == "download":
            self._from_directory = self._step.directory
            self._to_directory = self._work_directory
        if self._direction == "upload":
            self._from_directory = self._work_directory
            self._to_directory = self._step.directory

    def _get_files(self) -> list[str]:
        out_files = []
        out_files = os.listdir(self._from_directory)
        return out_files

    def _rename_files(self, in_files: list[str]) -> list[str]:
        out_files = []
        for filename in in_files:
            from_filename = filename
            to_filename = filename + ".processing"
            os.rename(
                os.path.join(self._from_directory, from_filename),
                os.path.join(self._from_directory, to_filename),
            )
            out_files.append(to_filename)
        return out_files

    def _download_files(self, in_files: list[str]) -> list[str]:
        out_files = []
        for filename in in_files:
            from_filename = filename
            to_filename = filename[:-11]

            with open(
                os.path.join(self._from_directory, from_filename), "rb"
            ) as file_bytes:
                file_data = file_bytes.read()
            with open(os.path.join(self._to_directory, to_filename), "wb") as f_byte:
                f_byte.write(file_data)

            os.remove(os.path.join(self._from_directory, from_filename))

            out_files.append(to_filename)
        return out_files

    def _upload_files(self, in_files: list[str]) -> list[str]:
        return self._download_files(in_files)

    def _disconnect(self):
        pass
