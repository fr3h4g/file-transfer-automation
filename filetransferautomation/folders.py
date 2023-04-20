"""Folders."""
from __future__ import annotations

import os

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

from filetransferautomation import settings
from filetransferautomation.shemas import Folder

router = APIRouter()

FOLDERS = []


def load_folders():
    """Load folders from database."""
    global FOLDERS
    FOLDERS.append(Folder(folder_id=1, name="test"))

    for folder in FOLDERS:
        path = os.path.join(settings.FOLDERS_DIR, folder.name)
        if not os.path.exists(path):
            os.makedirs(path)

    return FOLDERS


@router.get("")
def list_folders():
    """List folders."""
    return FOLDERS


@router.get("/{id}")
def get_folder(id: int) -> Folder | None:
    """Get a folder."""
    for folder in FOLDERS:
        if folder.folder_id == id:
            return folder
    return None


@router.get("/{id}/files")
def get_files(id: int):
    """List files in folder."""
    folder = get_folder(id)
    if not folder:
        return {"details": "folder not found."}
    files = os.listdir(os.path.join(settings.FOLDERS_DIR, folder.name))
    return files


# @router.post("")
# def create_folder(folder_name: str):
#     pass


# @router.delete("/{id}")
# def delete_folder(id: str):
#     pass


@router.post("/{id}/uploadfiles")
async def create_upload_files(id: int, files: list[UploadFile]):
    """Upload files to a folder."""
    folder = get_folder(id)
    if not folder:
        return {"details": "folder not found."}

    for file in files:
        if file.filename:
            with open(
                os.path.join(settings.FOLDERS_DIR, folder.name, file.filename), "wb"
            ) as new_file:
                new_file.write(file.file.read())

    return {"filenames": [file.filename for file in files]}


@router.get("/{id}/download/{filename}")
async def download_file(id: int, filename: str):
    """Download a file from folder."""
    folder = get_folder(id)
    if not folder:
        return {"error": "folder not found."}
    return FileResponse(
        path=os.path.join(settings.FOLDERS_DIR, folder.name, filename),
        filename=filename,
        media_type="application/octet-stream",
    )


def setup_std_folders():
    """Make std folders."""
    if not os.path.exists(settings.FOLDERS_DIR):
        os.makedirs(settings.FOLDERS_DIR)
    if not os.path.exists(settings.WORK_DIR):
        os.makedirs(settings.WORK_DIR)
