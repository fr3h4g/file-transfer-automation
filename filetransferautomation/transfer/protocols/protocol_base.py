"""Base protocol."""
from __future__ import annotations

import copy
import datetime
import logging
import os
import time
from typing import Literal
import uuid

from filetransferautomation import models
from filetransferautomation.common import compare_filter
from filetransferautomation.logs import add_file_log_entry
from filetransferautomation.shemas import File


class ProtocolBase:
    """Base class for protocol implementation."""

    def __init__(
        self,
        direction: Literal["download"] | Literal["upload"],
        task: models.Task,
        step: models.Step,
        work_directory: str,
        task_run_id: str,
    ):
        """Init protocol base class."""
        self._direction = direction
        self._task = task
        self._step = step
        self._work_directory = work_directory
        self._taks_run_id = task_run_id

        self._remote_directory = None

        self._rename_from = None
        self._rename_to = None

    def run(self) -> list[File]:
        """Run base class."""
        logging.info(f"Connecting to '{self._step.host.name}'.")
        connected = self._connect()
        if not connected:
            logging.error(f"Can't connect to '{self._step.host.name}'.")
            return []

        get_files_out = []
        if self._direction == "download":
            logging.info(
                f"Listing files in directory '{self._remote_directory}' to download."
            )
            get_files_out = self._list_files()
        else:
            logging.info(
                f"Listing files in work directory '{self._work_directory}' for upload."
            )
            get_files_out = self._list_work_files()

        logging.debug(f"Files in directory: {get_files_out}.")
        total_files = len(get_files_out)

        tag_files_in = get_files_out
        tag_files_out = []
        tag_files_out = self._tag_files(tag_files_in)

        compare_files_in = tag_files_out
        compare_files_out = []
        compare_files_out = self._compare_files(compare_files_in)
        matched_files = len(compare_files_out)
        logging.info(
            f"Matched {matched_files} files of total {total_files} "
            f"files on filemask '{self._step.file_mask}'."
        )
        logging.debug(f"Matched files: {compare_files_out}.")

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
                start_time = time.time()
                download_files_out = self.__download_files(download_files_in)
                sum_bytes = sum(
                    [file.size if file.size else 0 for file in download_files_out]
                )
                duration = time.time() - start_time
                downloaded_files = len(download_files_out)
                logging.info(
                    f"Downloaded {downloaded_files} files, {sum_bytes} bytes "
                    f"from '{self._remote_directory}'. "
                    f"Duration: {round(duration,2)} seconds. "
                    f"{round(sum_bytes / duration, 0)} bytes/sec."
                )

                renamed_files_in = download_files_out
                rename_files_out = []
                rename_files_out = self._rename_work_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                update_files_in = rename_files_out
                update_files_out = []
                update_files_out = self._update_files_info(update_files_in)

                done_files = update_files_out
                logging.debug(f"Done files {done_files}.")
            else:
                renamed_files_in = compare_files_out
                rename_files_out = []
                rename_files_out = self._rename_work_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                update_files_in = rename_files_out
                update_files_out = []
                update_files_out = self._update_files_info(update_files_in)

                upload_files_in = update_files_out
                upload_files_out = []
                logging.info(f"Uploading {renamed_files} files.")
                start_time = time.time()
                upload_files_out = self.__upload_files(upload_files_in)
                sum_bytes = sum(
                    [file.size if file.size else 0 for file in upload_files_out]
                )
                duration = time.time() - start_time
                uploaded_files = len(upload_files_out)
                logging.info(
                    f"Uploaded {uploaded_files} files, {sum_bytes} bytes "
                    f"to '{self._remote_directory}'. "
                    f"Duration: {round(duration,2)} seconds. "
                    f"{round(sum_bytes / duration, 0)} bytes/sec."
                )

                renamed_files_in = upload_files_out
                rename_files_out = []
                rename_files_out = self._rename_remote_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                done_files = rename_files_out
                logging.debug(f"Done files {done_files}.")
        else:
            logging.info("No files found to retrieve.")

        self._disconnect_from_remote()
        logging.info(f"Disconnected from '{self._step.host.name}'.")

        return done_files

    def _connect(self) -> bool:
        return True

    def _tag_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            file.task_id = self._task.task_id
            if not file.file_id:
                file.file_id = str(uuid.uuid4())
            out_files.append(file)
        return out_files

    def _update_files_info(self, in_files: list[File]) -> list[File]:
        if not self._work_directory:
            raise ValueError("_work_directory is not set.")
        out_files = []
        for file in in_files:
            file.size = os.path.getsize(os.path.join(self._work_directory, file.name))
            if not file.timestamp:
                file_time = os.path.getctime(
                    os.path.join(self._work_directory, file.name)
                )
                file.timestamp = datetime.datetime.fromtimestamp(file_time)
            else:
                file_time = file.timestamp.timestamp()
                os.utime(
                    os.path.join(self._work_directory, file.name),
                    times=(file_time, file_time),
                )
            out_files.append(file)
        return out_files

    def _list_files(self) -> list[File]:
        return []

    def _list_work_files(self) -> list[File]:
        if not self._work_directory:
            raise ValueError("_work_directory is not set.")
        out_files = []
        for file in [File(file) for file in os.listdir(self._work_directory)]:
            file.size = os.path.getsize(os.path.join(self._work_directory, file.name))
            if not file.timestamp:
                file.timestamp = datetime.datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(self._work_directory, file.name))
                )
            out_files.append(file)
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
            file_out = self._rename_file(copy.copy(file))
            if file_out:
                file_out.name = self._rename_to
                out_files.append(file_out)
                logging.debug(f"Renamed remote file {file} to {file_out}.")
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
            file_out = self._rename_work_file(copy.copy(file))
            if file_out:
                file_out.name = self._rename_to
                out_files.append(file_out)
                logging.debug(f"Renamed work file {file} to {file_out}.")
        return out_files

    def _rename_work_file(self, file: File) -> File:
        if not self._work_directory:
            raise ValueError("_work_directory is not set.")
        if not self._rename_from:
            raise ValueError("_rename_from is not set.")
        if not self._rename_to:
            raise ValueError("_rename_to is not set.")
        os.rename(
            os.path.join(self._work_directory, self._rename_from),
            os.path.join(self._work_directory, self._rename_to),
        )
        file.name = self._rename_to
        return file

    def __download_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            logging.debug(f"Started downloading {file}.")
            add_file_log_entry(
                task_run_id=self._taks_run_id,
                task_id=self._task.task_id,
                step_id=self._step.step_id,
                file=file,
                status="downloading",
            )
            file = self._download_file(file)
            logging.debug(f"File downloaded {file}.")
            add_file_log_entry(
                task_run_id=self._taks_run_id,
                task_id=self._task.task_id,
                step_id=self._step.step_id,
                file=file,
                status="downloaded",
            )
            if file:
                out_files.append(file)
                self._delete_file(file)
                logging.debug(f"Remote file deleted {file}.")
        return out_files

    def _download_file(self, file: File) -> File:
        return file

    def __upload_files(self, in_files: list[File]) -> list[File]:
        out_files = []
        for file in in_files:
            logging.debug(f"Started uploading {file}.")
            add_file_log_entry(
                task_run_id=self._taks_run_id,
                task_id=self._task.task_id,
                step_id=self._step.step_id,
                file=file,
                status="uploading",
            )
            file = self._upload_file(file)
            logging.debug(f"File uploaded {file}.")
            add_file_log_entry(
                task_run_id=self._taks_run_id,
                task_id=self._task.task_id,
                step_id=self._step.step_id,
                file=file,
                status="uploaded",
            )
            if file:
                out_files.append(file)
                self._delete_work_file(file)
                logging.debug(f"Work file deleted {file}.")
        return out_files

    def _upload_file(self, file: File) -> File:
        return file

    def _disconnect_from_remote(self):
        pass
