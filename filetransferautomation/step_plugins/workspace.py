"""Workspace plugin."""
import os

from pydantic import BaseModel

from filetransferautomation import settings
from filetransferautomation.plugin_collection import Plugin


class WorkspaceInput(BaseModel):
    """Input data model."""

    workspace_id: str


class CreateWorkspace(Plugin):
    """Create workspace plugin."""

    name = "create_workspace"
    input_model = WorkspaceInput
    output_model = None
    arguments = input_model

    def process(self):
        """Create workspace."""
        work_directory = os.path.join(settings.WORK_DIR, self.arguments.workspace_id)
        os.mkdir(work_directory)
        print("created workspace", self.arguments.workspace_id)


class DeleteWorkspace(Plugin):
    """Delete workspace plugin."""

    name = "delete_workspace"
    input_model = WorkspaceInput
    arguments = input_model

    def process(self):
        """Delete workspace."""
        work_directory = os.path.join(settings.WORK_DIR, self.arguments.workspace_id)
        os.rmdir(work_directory)
        print("deleted workspace", self.arguments.workspace_id)
