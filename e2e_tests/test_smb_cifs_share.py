"""Test against smb_cifs_share docker image."""
from filetransferautomation import models
from filetransferautomation.database import engine
from filetransferautomation.models import Host
from filetransferautomation.step_plugins.smb_cifs import Download, Upload

"""
docker run --name smb_cifs -it -p 139:139 -p 445:445 -d dperson/samba -p \
    -u "bob;12345" \
    -s "bob;/bob;yes;no;no;bob"
"""

USER = "bob"
HOST = "localhost"
PASS = "12345"


def test_db_setup():
    """Setup db."""
    models.Base.metadata.create_all(bind=engine)


def test_smb_cifs_share_upload():
    """smb_cifs_share upload test."""
    host = Host(username="bob", password="12345", share="\\\\localhost\\bob")
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


def test_smb_cifs_share_download():
    """smb_cifs_share download test."""
    host = Host(username="bob", password="12345", share="\\\\localhost\\bob")
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
