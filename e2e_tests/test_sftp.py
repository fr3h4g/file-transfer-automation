"""Test against SFTP docker image."""
from filetransferautomation import models
from filetransferautomation.database import engine
from filetransferautomation.models import Host
from filetransferautomation.step_plugins.sftp import Download, Upload

"""
docker run --name sftp -v ${PWD}/e2e_data/sftp.json:/app/config/sftp.json:ro \
    -p 2222:22 -d emberstack/sftp
"""

USER = "bob"
HOST = "localhost"
PASS = "12345"


def test_db_setup():
    """Setup db."""
    models.Base.metadata.create_all(bind=engine)


def test_sftp_upload():
    """SFTP upload test."""
    with open("test.txt", "w") as file:
        file.write("123åäö")

    host = Host(
        username=USER,
        password=PASS,
        host=HOST,
        port=2222,
        directory="",
    )
    download = Upload(
        arguments='{"file_filter":"test.txt", "delete_files":true}',
        variables={
            "host": host,
            "workspace_directory": ".",
            "workspace_id": "test",
            "step_id": 1,
            "task_id": 1,
        },
    )
    download.process()


def test_sftp_download():
    """SFTP download test."""
    host = Host(
        username=USER,
        password=PASS,
        host=HOST,
        port=2222,
        directory="",
    )
    download = Download(
        arguments='{"file_filter":"test.txt", "delete_files":true}',
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
