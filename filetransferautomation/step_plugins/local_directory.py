"""Workspace plugin."""
import logging
import os
import time

from pydantic import BaseModel

from filetransferautomation.common import compare_filter
from filetransferautomation.hosts import get_host
from filetransferautomation.logs import add_file_log_entry
from filetransferautomation.plugin_collection import Plugin


class Input(BaseModel):
    """Input data model."""

    file_filter: str | None = "*.*"
    delete_files: bool | None = False


class Output(BaseModel):
    """Output data model."""

    found_files: list[str]
    matched_files: list[str]
    downloaded_files: list[str] | None
    uploaded_files: list[str] | None


class ListFiles(Plugin):
    """List files in local directory."""

    input_model = Input
    output_model = Output
    arguments = input_model

    def process(self):
        """List files in local directory."""
        if "host" in self.variables:
            host = self.get_variable("host")
        else:
            host = get_host(self.get_variable("host_id"))
        if not self.arguments.file_filter:
            raise ValueError("argument file_filter can't be empty.")
        matched_files = []
        files = []
        if host:
            files = os.listdir(host.directory)
            for file in files:
                if compare_filter(file, self.arguments.file_filter):
                    matched_files.append(file)
        self.set_variable("found_files", files)
        self.set_variable("matched_files", matched_files)


class DownloadFiles(Plugin):
    """Download files from local directory."""

    input_model = Input
    output_model = Output
    arguments = input_model

    def process(self):
        """Download files from local directory."""

        error = False

        if "host" in self.variables:
            host = self.get_variable("host")
        else:
            host = get_host(self.get_variable("host_id"))
        if not host:
            return None
        if not host.directory:
            return None
        if not self.arguments.file_filter:
            raise ValueError("argument file_filter can't be empty.")
        if self.arguments.delete_files not in (True, False):
            raise ValueError("argument delete_files must be True or False.")

        remote_directory = host.directory
        workspace_directory = self.get_variable("workspace_directory")
        files_to_download = []
        files = []
        downloaded_files = []

        if host:
            files = os.listdir(remote_directory)
            for file in files:
                if compare_filter(file, self.arguments.file_filter):
                    files_to_download.append(file)

        for file in files_to_download:
            add_file_log_entry(
                task_run_id=self.get_variable("workspace_id"),
                task_id=self.get_variable("task_id"),
                step_id=self.get_variable("step_id"),
                filename=file,
                status="downloading",
            )

        for file in files_to_download:
            try:
                start_time = time.time()
                with open(os.path.join(remote_directory, file), "rb") as from_file:
                    file_data = from_file.read()
                with open(os.path.join(workspace_directory, file), "wb") as to_file:
                    to_file.write(file_data)
            except Exception:
                add_file_log_entry(
                    task_run_id=self.get_variable("workspace_id"),
                    task_id=self.get_variable("task_id"),
                    step_id=self.get_variable("step_id"),
                    filename=file,
                    status="error",
                )
                error = True
            else:
                size = os.path.getsize(os.path.join(workspace_directory, file))
                duration = time.time() - start_time

                add_file_log_entry(
                    task_run_id=self.get_variable("workspace_id"),
                    task_id=self.get_variable("task_id"),
                    step_id=self.get_variable("step_id"),
                    filename=file,
                    status="downloaded",
                    filesize=size,
                    duration_sec=duration,
                    bytes_per_sec=size / duration,
                )
                downloaded_files.append(file)

        logging.info(f"Downloaded files {downloaded_files} from '{host.name}'.")

        if self.arguments.delete_files:
            for file in downloaded_files:
                os.remove(os.path.join(remote_directory, file))

        self.set_variable("found_files", files)
        self.set_variable("matched_files", files_to_download)
        self.set_variable("downloaded_files", downloaded_files)

        if error:
            raise Exception("error in file transfer")


class UploadFiles(Plugin):
    """Upload files to local directory."""

    input_model = Input
    output_model = Output
    arguments = input_model

    def process(self):
        """Upload files to local directory."""

        error = False

        if "host" in self.variables:
            host = self.get_variable("host")
        else:
            host = get_host(self.get_variable("host_id"))
        if not host:
            return None
        if not host.directory:
            return None
        if not self.arguments.file_filter:
            raise ValueError("argument file_filter can't be empty.")
        if self.arguments.delete_files not in (True, False):
            raise ValueError("argument delete_files must be True or False.")

        remote_directory = host.directory
        workspace_directory = self.get_variable("workspace_directory")
        files_to_upload = []
        files = []
        uploaded_files = []

        if host:
            files = os.listdir(workspace_directory)
            for file in files:
                if compare_filter(file, self.arguments.file_filter):
                    files_to_upload.append(file)

        for file in files_to_upload:
            add_file_log_entry(
                task_run_id=self.get_variable("workspace_id"),
                task_id=self.get_variable("task_id"),
                step_id=self.get_variable("step_id"),
                filename=file,
                status="uploading",
            )

        for file in files_to_upload:
            try:
                start_time = time.time()
                with open(os.path.join(workspace_directory, file), "rb") as from_file:
                    file_data = from_file.read()
                with open(os.path.join(remote_directory, file), "wb") as to_file:
                    to_file.write(file_data)
            except Exception:
                add_file_log_entry(
                    task_run_id=self.get_variable("workspace_id"),
                    task_id=self.get_variable("task_id"),
                    step_id=self.get_variable("step_id"),
                    filename=file,
                    status="error",
                )
                error = True
            else:
                uploaded_files.append(file)
                size = os.path.getsize(os.path.join(workspace_directory, file))
                duration = time.time() - start_time

                add_file_log_entry(
                    task_run_id=self.get_variable("workspace_id"),
                    task_id=self.get_variable("task_id"),
                    step_id=self.get_variable("step_id"),
                    filename=file,
                    status="uploaded",
                    duration_sec=duration,
                    filesize=size,
                    bytes_per_sec=size / duration,
                )

        logging.info(f"Uploaded files {uploaded_files} to '{host.name}'.")

        if self.arguments.delete_files:
            for file in uploaded_files:
                os.remove(os.path.join(workspace_directory, file))

        self.set_variable("found_files", files)
        self.set_variable("matched_files", files_to_upload)
        self.set_variable("uploaded_files", uploaded_files)

        if error:
            raise Exception("error in file transfer")
