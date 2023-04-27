"""SFTP plugin."""
import io
import logging
import os
import time

from pydantic import BaseModel
import pysftp

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


class Download(Plugin):
    """Download file from SFTP."""

    input_model = Input
    output_model = Output
    arguments = input_model

    def process(self):
        """Download file from SFTP."""
        if "host" in self.variables:
            host = self.get_variable("host")
        else:
            host = get_host(self.get_variable("host_id"))
        if not host:
            return None

        workspace_directory = self.get_variable("workspace_directory")
        files_to_download = []
        files = []
        downloaded_files = []

        if host and host.host and host.username and host.password:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None  # type: ignore
            with pysftp.Connection(
                host.host,
                username=host.username,
                password=host.password,
                port=host.port if host.port else 22,
                cnopts=cnopts,
            ) as sftp:
                if host.directory:
                    sftp.chdir(host.directory)

                files = sftp.listdir()
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

                    start_time = time.time()

                    fo_data = io.BytesIO()
                    sftp.getfo(file, fo_data)
                    fo_data.seek(0)

                    with open(os.path.join(workspace_directory, file), "wb") as to_file:
                        to_file.write(fo_data.read())

                    downloaded_files.append(file)
                    size = os.path.getsize(os.path.join(workspace_directory, file))
                    duration = time.time() - start_time

                    add_file_log_entry(
                        task_run_id=self.get_variable("workspace_id"),
                        task_id=self.get_variable("task_id"),
                        step_id=self.get_variable("step_id"),
                        filename=file,
                        status="downloaded",
                        duration_sec=duration,
                        filesize=size,
                        bytes_per_sec=size / duration,
                    )

                if self.arguments.delete_files:
                    for file in downloaded_files:
                        sftp.remove(file)

        logging.info(f"Downloaded files {downloaded_files} from '{host.name}'.")

        self.set_variable("found_files", files)
        self.set_variable("matched_files", files_to_download)
        self.set_variable("downloaded_files", downloaded_files)


class Upload(Plugin):
    """Upload file to SFTP."""

    input_model = Input
    output_model = Output
    arguments = input_model

    def process(self):
        """Upload file to SFTP."""
        if "host" in self.variables:
            host = self.get_variable("host")
        else:
            host = get_host(self.get_variable("host_id"))
        if not host:
            return None

        workspace_directory = self.get_variable("workspace_directory")
        files_to_upload = []
        files = []
        uploaded_files = []

        if host and host.host and host.username and host.password:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None  # type: ignore
            with pysftp.Connection(
                host.host,
                username=host.username,
                password=host.password,
                port=host.port if host.port else 22,
                cnopts=cnopts,
            ) as sftp:
                if host.directory:
                    sftp.chdir(host.directory)

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

                    start_time = time.time()
                    with open(
                        os.path.join(workspace_directory, file), "rb"
                    ) as from_file:
                        if not host.directory:
                            host.directory = "."
                        filename = str(os.path.join(host.directory, file)) + ".tmp"

                        if sftp.exists(filename[:-4]):
                            sftp.unlink(filename[:-4])

                        sftp.putfo(from_file, f"{filename}")

                        sftp.rename(filename, filename[:-4])

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
