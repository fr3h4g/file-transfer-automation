"""Test against docker images."""
from filetransferautomation.models import Host
from filetransferautomation.step_plugins.ftp import Download, Upload

"""
docker run -d --name ftpd_server -p 21:21 -p 30000-30009:30000-30009 /
    -e FTP_USER_NAME=bob /
    -e FTP_USER_PASS=12345 /
    -e FTP_USER_HOME=/home/bob /
    -e "PUBLICHOST=localhost" /
    stilliard/pure-ftpd
"""


def test_ftp_upload():
    """FTP upload test."""
    host = Host(
        username="bob",
        password="12345",
        host="localhost",
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
