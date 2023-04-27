"""Test against FTP docker image."""
from filetransferautomation import models
from filetransferautomation.database import engine
from filetransferautomation.models import Host
from filetransferautomation.step_plugins.ftp import Download, Upload

"""
docker run -d --name ftp -p 2221:21 -p 30000-30009:30000-30009 \
    -e FTP_USER_NAME=bob \
    -e FTP_USER_PASS=12345 \
    -e FTP_USER_HOME=/home/bob \
    -e "PUBLICHOST=localhost" \
    stilliard/pure-ftpd
"""

USER = "bob"
HOST = "localhost"
PASS = "12345"


def test_db_setup():
    """Setup db."""
    models.Base.metadata.create_all(bind=engine)


def test_ftp_upload():
    """FTP upload test."""
    with open("test.txt", "w") as file:
        file.write("123åäö")

    host = Host(
        username="bob",
        password="12345",
        host="localhost",
        port=2221,
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


def test_ftp_download():
    """FTP download test."""
    host = Host(
        username="bob",
        password="12345",
        host="localhost",
        port=2221,
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
