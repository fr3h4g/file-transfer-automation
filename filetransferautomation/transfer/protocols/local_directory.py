"""Local directory protocol."""
from __future__ import annotations
import os

from filetransferautomation.models import File
import copy
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
        out_files = []
        out_files = [File(file) for file in os.listdir(self._from_directory)]
        return out_files

    def _rename_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        if not self._from_directory or not self._to_directory:
            return out_files
        for filename in in_files:
            from_filename = filename
            to_filename = copy.deepcopy(filename)
            to_filename.name = to_filename.name + ".processing"
            os.rename(
                os.path.join(self._from_directory, from_filename.name),
                os.path.join(self._from_directory, to_filename.name),
            )
            out_files.append(to_filename)
        return out_files

    def _download_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        if not self._from_directory or not self._to_directory:
            return out_files
        for filename in in_files:
            from_filename = filename
            to_filename = copy.deepcopy(filename)
            to_filename.name = to_filename.name[:-11]

            with open(
                os.path.join(self._from_directory, from_filename.name), "rb"
            ) as file_bytes:
                file_data = file_bytes.read()
            with open(
                os.path.join(self._to_directory, to_filename.name), "wb"
            ) as f_byte:
                f_byte.write(file_data)

            os.remove(os.path.join(self._from_directory, from_filename.name))

            out_files.append(to_filename)
        return out_files

    def _upload_files(self, in_files: list[File]) -> list[File]:
        return self._download_files(in_files)

    def _disconnect(self):
        pass
