"""Local directory protocol."""
from __future__ import annotations

import os

from filetransferautomation.models import File

from .base_protocol import BaseProtocol


class LocalDirectory(BaseProtocol):
    """Local directory protocol."""

    def _connect_to_remote(self) -> bool:
        self._remote_directory = self._step.directory
        return True

    def _list_remote_files(self) -> list[File]:
        out_files = [File(file) for file in os.listdir(self._remote_directory)]
        return out_files

    def _delete_remote_file(self, file: File) -> bool:
        os.remove(os.path.join(self._remote_directory, file.name + ".processing"))
        return True

    def _rename_remote_file(self, file: File) -> File:
        os.rename(
            os.path.join(self._remote_directory, self._rename_from),
            os.path.join(self._remote_directory, self._rename_to),
        )
        return file

    def _download_remote_file(self, file: File) -> File | None:
        with open(
            os.path.join(self._remote_directory, file.name + ".processing"), "rb"
        ) as from_file:
            file_data = from_file.read()
        with open(
            os.path.join(self._work_directory, file.name + ".processing"), "wb"
        ) as to_file:
            to_file.write(file_data)
        return file

    def _upload_remote_file(self, file: File) -> File | None:
        with open(
            os.path.join(self._work_directory, file.name + ".processing"), "rb"
        ) as from_file:
            file_data = from_file.read()
        with open(
            os.path.join(self._remote_directory, file.name + ".processing"), "wb"
        ) as to_file:
            to_file.write(file_data)
        return file

    def _disconnect_from_remote(self):
        pass
