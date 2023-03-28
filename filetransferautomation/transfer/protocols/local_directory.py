"""Local directory protocol."""
from __future__ import annotations

import os

from filetransferautomation.models import File

from .base_protocol import BaseProtocol


class LocalDirectory(BaseProtocol):
    """Local directory protocol."""

    def _connect(self) -> bool:
        if self._direction == "download":
            self._from_directory = self._step.directory
            self._to_directory = self._work_directory
        if self._direction == "upload":
            self._from_directory = self._work_directory
            self._to_directory = self._step.directory
        return True

    def _list_files(self) -> list[File]:
        out_files = [File(file) for file in os.listdir(self._from_directory)]
        return out_files

    def _rename_remote_file(self, file: File) -> File:
        if self._direction == "download":
            os.rename(
                os.path.join(self._from_directory, file.name),
                os.path.join(self._from_directory, file.name + ".processing"),
            )
        else:
            os.rename(
                os.path.join(self._to_directory, file.name + ".processing"),
                os.path.join(self._to_directory, file.name),
            )
        return file

    def _download_file(self, file: File) -> File | None:
        with open(
            os.path.join(self._from_directory, file.name + ".processing"), "rb"
        ) as from_file:
            file_data = from_file.read()
        with open(
            os.path.join(self._to_directory, file.name + ".processing"), "wb"
        ) as to_file:
            to_file.write(file_data)
        os.remove(os.path.join(self._from_directory, file.name + ".processing"))
        return file

    def _upload_file(self, file: File) -> File | None:
        with open(
            os.path.join(self._from_directory, file.name + ".processing"), "rb"
        ) as from_file:
            file_data = from_file.read()
        with open(
            os.path.join(self._to_directory, file.name + ".processing"), "wb"
        ) as to_file:
            to_file.write(file_data)
        os.remove(os.path.join(self._from_directory, file.name + ".processing"))
        return file

    def _disconnect(self):
        pass
