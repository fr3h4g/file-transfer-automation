"""Base protocol."""
from __future__ import annotations
import logging

from typing import Literal

from filetransferautomation import steps, tasks
from filetransferautomation.common import compare_filter


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

        self._from_directory = None
        self._to_directory = None

    def run(self) -> list[str]:
        """Run base class."""
        logging.info(f"Connecting to '{self._task.name}'.")
        connected = self._connect()
        if not connected:
            logging.error(f"Can't connect to '{self._task.name}'.")
            return []

        if self._direction == "download":
            logging.info(
                f"Listing files in directory '{self._from_directory}' on "
                f"'{self._task.name}' to download."
            )
        else:
            logging.info(
                f"Listing files in work directory for upload to '{self._task.name}'."
            )
        get_files_out = []
        get_files_out = self._get_files()
        total_files = len(get_files_out)

        compare_files_in = get_files_out
        compare_files_out = []
        compare_files_out = self._compare_files(compare_files_in)
        matched_files = len(compare_files_out)
        logging.info(f"Matched {matched_files} files of total {total_files} files.")

        done_files = []

        if compare_files_out:
            if self._direction == "download":
                self._to_directory = self._work_directory

                renamed_files_in = compare_files_out
                rename_files_out = []
                rename_files_out = self._rename_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                download_files_in = rename_files_out
                download_files_out = []
                logging.info(f"Downloading {renamed_files} files.")
                download_files_out = self._download_files(download_files_in)
                downloaded_files = len(download_files_out)
                logging.info(
                    f"Downloaded {downloaded_files} files from '{self._from_directory}'."
                )

                done_files = download_files_out

            else:
                self._from_directory = self._work_directory

                renamed_files_in = compare_files_out
                rename_files_out = []
                rename_files_out = self._rename_files(renamed_files_in)
                renamed_files = len(rename_files_out)

                upload_files_in = rename_files_out
                upload_files_out = []
                logging.info(f"Uploading {renamed_files} files.")
                upload_files_out = self._upload_files(upload_files_in)
                uploaded_files = len(upload_files_out)
                logging.info(
                    f"Uploaded {uploaded_files} files to '{self._to_directory}'."
                )

                done_files = upload_files_out
        else:
            logging.info(f"No files found to transfer.")

        self._disconnect()
        logging.info(f"Disconnected from '{self._task.name}'.")

        return done_files

    def _connect(self) -> bool:
        return True

    def _get_files(self) -> list[str]:
        return []

    def _compare_files(self, in_files: list[str]) -> list[str]:
        out_files = []
        for filename in in_files:
            if compare_filter(filename, self._step.file_mask):
                out_files.append(filename)
        return out_files

    def _rename_files(self, in_files: list[str]) -> list[str]:
        out_files = []
        out_files = in_files
        return out_files

    def _download_files(self, in_files: list[str]) -> list[str]:
        out_files = []
        out_files = in_files
        return out_files

    def _upload_files(self, in_files: list[str]) -> list[str]:
        out_files = []
        out_files = in_files
        return out_files

    def _disconnect(self):
        pass
