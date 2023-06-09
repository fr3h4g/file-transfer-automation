"""Test against FTP docker image."""
from filetransferautomation import models
from filetransferautomation.database import engine
from filetransferautomation.models import Host
from filetransferautomation.step_plugins.local_directory import (
    DownloadFiles,
    UploadFiles,
)


def test_db_setup():
    """Setup db."""
    models.Base.metadata.create_all(bind=engine)


def test_local_directory_upload():
    """local_directory upload test."""
    with open("test.txt", "w") as file:
        file.write("123åäö")

    host = Host(
        directory=".",
    )
    download = UploadFiles(
        arguments='{"file_filter":"test.txt", "delete_files":false}',
        variables={
            "host": host,
            "workspace_directory": ".",
            "workspace_id": "test",
            "step_id": 1,
            "task_id": 1,
        },
    )
    download.process()


def test_local_directory_download():
    """local_directory download test."""
    host = Host(
        directory=".",
    )
    download = DownloadFiles(
        arguments='{"file_filter":"test.txt", "delete_files":false}',
        variables={
            "host": host,
            "workspace_directory": ".",
            "workspace_id": "test",
            "step_id": 1,
            "task_id": 1,
        },
    )
    download.process()

    with open("test.txt") as file:
        assert file.read() == "123åäö"
