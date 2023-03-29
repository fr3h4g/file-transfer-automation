"""Local directory protocol."""
from __future__ import annotations

import os

from filetransferautomation.models import File

from .protocol_base import ProtocolBase


class LocalDirectory(ProtocolBase):
    """Local directory protocol."""

    def _connect(self) -> bool:
        self._remote_directory = self._step.directory
        return True

    def _list_files(self) -> list[File]:
        out_files = [File(file) for file in os.listdir(self._remote_directory)]
        return out_files

    def _delete_file(self, file: File) -> bool:
        if not self._remote_directory:
            raise ValueError("_remote_directory is not set.")
        os.remove(os.path.join(self._remote_directory, file.name))
        return True

    def _rename_file(self, file: File) -> File:
        if not self._remote_directory:
            raise ValueError("_remote_directory is not set.")
        if not self._rename_from:
            raise ValueError("_rename_from is not set.")
        if not self._rename_to:
            raise ValueError("_rename_to is not set.")
        os.rename(
            os.path.join(self._remote_directory, self._rename_from),
            os.path.join(self._remote_directory, self._rename_to),
        )
        file.name = self._rename_to
        return file

    def _download_file(self, file: File) -> File | None:
        if not self._remote_directory:
            raise ValueError("_remote_directory is not set.")
        with open(os.path.join(self._remote_directory, file.name), "rb") as from_file:
            file_data = from_file.read()
        with open(os.path.join(self._work_directory, file.name), "wb") as to_file:
            to_file.write(file_data)
        return file

    def _upload_file(self, file: File) -> File | None:
        if not self._remote_directory:
            raise ValueError("_remote_directory is not set.")
        with open(os.path.join(self._work_directory, file.name), "rb") as from_file:
            file_data = from_file.read()
        with open(os.path.join(self._remote_directory, file.name), "wb") as to_file:
            to_file.write(file_data)
        return file

    def _disconnect_from_remote(self):
        pass
