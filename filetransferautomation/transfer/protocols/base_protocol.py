"""Base protocol."""
from __future__ import annotations

import logging
import os
from typing import Literal

from filetransferautomation import steps, tasks
from filetransferautomation.common import compare_filter
from filetransferautomation.models import File


class BaseProtocol:
    """Base class for protocol implementation."""

    def __init__(
        self,
        direction: Literal["download"] | Literal["upload"],
        task: tasks.Task,
        step: steps.Step,
        work_directory: str,
    ):
        """Init protocol base class."""
        self._direction = direction
        self._task = task
        self._step = step
        self._work_directory = work_directory

        self._remote_directory = None

        self._rename_from = None
        self._rename_to = None

    def run(self) -> list[File]:
        """Run base class."""
        logging.info(f"Connecting to '{self._step.name}'.")
        connected = self._connect()
        if not connected:
            logging.error(f"Can't connect to '{self._step.name}'.")
            return []

        get_files_out = []
        if self._direction == "download":
            logging.info(
                f"Listing files in directory '{self._remote_directory}' to download."
            )
            get_files_out = self._list_files()
            total_files = len(get_files_out)
        else:
            logging.info(
                f"Listing files in work directory '{self._work_directory}' for upload."
            )
            get_files_out = self._list_work_files()
            total_files = len(get_files_out)

        compare_files_in = get_files_out
        compare_files_out = []
        compare_files_out = self._compare_files(compare_files_in)
        matched_files = len(compare_files_out)
        logging.info(f"Matched {matched_files} files of total {total_files} files.")

        done_files = []

        if compare_files_out:
            if self._direction == "download":
                renamed_files_in = compare_files_out
                rename_files_out = []
                rename_files_out = self._rename_remote_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                download_files_in = rename_files_out
                download_files_out = []
                logging.info(f"Downloading {renamed_files} files.")
                download_files_out = self.__download_files(download_files_in)
                downloaded_files = len(download_files_out)
                logging.info(
                    f"Downloaded {downloaded_files} files from '{self._remote_directory}'."
                )

                renamed_files_in = download_files_out
                rename_files_out = []
                rename_files_out = self._rename_work_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                done_files = rename_files_out

            else:
                renamed_files_in = compare_files_out
                rename_files_out = []
                rename_files_out = self._rename_work_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                upload_files_in = rename_files_out
                upload_files_out = []
                logging.info(f"Uploading {renamed_files} files.")
                upload_files_out = self.__upload_files(upload_files_in)
                uploaded_files = len(upload_files_out)
                logging.info(
                    f"Uploaded {uploaded_files} files to '{self._remote_directory}'."
                )

                renamed_files_in = upload_files_out
                rename_files_out = []
                rename_files_out = self._rename_remote_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                done_files = rename_files_out
        else:
            logging.info("No files found to transfer.")

        self._disconnect_from_remote()
        logging.info(f"Disconnected from '{self._step.name}'.")

        return done_files

    def _connect(self) -> bool:
        return True

    def _list_files(self) -> list[File]:
        return []

    def _list_work_files(self) -> list[File]:
        out_files = [File(file) for file in os.listdir(self._work_directory)]
        return out_files

    def _compare_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for filename in in_files:
            if compare_filter(filename.name, self._step.file_mask):
                out_files.append(filename)
        return out_files

    def _rename_remote_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            if self._direction == "download":
                self._rename_from = file.name
                self._rename_to = file.name + ".processing"
            else:
                self._rename_from = file.name
                self._rename_to = file.name[:-11]
            file = self._rename_file(file)
            if file:
                file.name = self._rename_to
                out_files.append(file)
                logging.debug(f"Remote file renamed {file}")
        return out_files

    def _delete_file(self, file: File) -> bool:
        return True

    def _delete_work_file(self, file: File) -> bool:
        os.remove(os.path.join(self._work_directory, file.name))
        return True

    def _rename_file(self, file: File) -> File:
        return file

    def _rename_work_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            if self._direction == "download":
                self._rename_from = file.name
                self._rename_to = file.name[:-11]
            else:
                self._rename_from = file.name
                self._rename_to = file.name + ".processing"
            file = self._rename_work_file(file)
            if file:
                file.name = self._rename_to
                out_files.append(file)
        return out_files

    def _rename_work_file(self, file: File) -> File:
        os.rename(
            os.path.join(self._work_directory, self._rename_from),
            os.path.join(self._work_directory, self._rename_to),
        )
        file.name = file.name
        return file

    def __download_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            file = self._download_file(file)
            logging.debug(f"File downloaded {file}.")
            if file:
                out_files.append(file)
                self._delete_file(file)
                logging.debug(f"Remote file deleted {file}.")
        return out_files

    def _download_file(self, file: File) -> File | None:
        return file

    def __upload_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            file = self._upload_file(file)
            logging.debug(f"File uploaded {file}.")
            if file:
                out_files.append(file)
                self._delete_work_file(file)
                logging.debug(f"Work file deleted {file}.")
        return out_files

    def _upload_file(self, file: File) -> File | None:
        return file

    def _disconnect_from_remote(self):
        pass
