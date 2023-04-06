"""Workspace plugin."""
import logging
import os
import shutil

from pydantic import BaseModel

from filetransferautomation.plugin_collection import Plugin


class WorkspaceInput(BaseModel):
    """Input data model."""

    ...


class WorkspaceOutput(BaseModel):
    """Output data model."""

    ...


class Create(Plugin):
    """Create workspace plugin."""

    input_model = WorkspaceInput
    output_model = WorkspaceOutput
    arguments = input_model

    def process(self):
        """Create workspace."""
        work_directory = self.get_variable("workspace_directory")
        os.mkdir(work_directory)
        logging.info("Created workspace directory ", work_directory)


class Delete(Plugin):
    """Delete workspace plugin."""

    input_model = WorkspaceInput
    output_model = WorkspaceOutput
    arguments = input_model

    def process(self):
        """Delete workspace."""
        work_directory = self.get_variable("workspace_directory")
        shutil.rmtree(work_directory)
        logging.info("Deleted workspace directory ", work_directory)
