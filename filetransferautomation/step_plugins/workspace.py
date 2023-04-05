"""Workspace plugin."""
import os

from pydantic import BaseModel

from filetransferautomation import settings
from filetransferautomation.plugin_collection import Plugin


class WorkspaceInput(BaseModel):
    """Input data model."""

    ...


class WorkspaceOutput(BaseModel):
    """Output data model."""

    ...


class CreateWorkspace(Plugin):
    """Create workspace plugin."""

    name = "create_workspace"
    input_model = WorkspaceInput
    output_model = WorkspaceOutput
    arguments = input_model

    def process(self):
        """Create workspace."""
        work_directory = os.path.join(
            settings.WORK_DIR, self.get_variable("workspace_id")
        )
        os.mkdir(work_directory)
        print("created workspace", self.get_variable("workspace_id"))


class DeleteWorkspace(Plugin):
    """Delete workspace plugin."""

    name = "delete_workspace"
    input_model = WorkspaceInput
    output_model = WorkspaceOutput
    arguments = input_model

    def process(self):
        """Delete workspace."""
        work_directory = os.path.join(
            settings.WORK_DIR, self.get_variable("workspace_id")
        )
        os.rmdir(work_directory)
        print("deleted workspace", self.get_variable("workspace_id"))
