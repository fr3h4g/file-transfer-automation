"""Workspace plugin."""
import os

from pydantic import BaseModel

from filetransferautomation.common import compare_filter
from filetransferautomation.hosts import get_host
from filetransferautomation.plugin_collection import Plugin


class GetFilesInput(BaseModel):
    """Input data model."""

    file_filter: str | None = None


class GetFilesOutput(BaseModel):
    """Output data model."""

    downloaded_files: list[str]
    found_files: list[str]


class GetFiles(Plugin):
    """Create workspace plugin."""

    input_model = GetFilesInput
    output_model = GetFilesOutput
    arguments = input_model

    def process(self):
        """Download files from local directory."""
        host = get_host(self.get_variable("host_id"))
        downloaded_files = []
        files = []
        if host:
            files = os.listdir(host.directory)
            for file in files:
                if compare_filter(file, self.arguments.file_filter):
                    downloaded_files.append(file)
        self.set_variable("found_files", files)
        self.set_variable("downloaded_files", downloaded_files)
