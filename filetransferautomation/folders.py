"""Folders."""
from __future__ import annotations

from dataclasses import dataclass
import os

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

router = APIRouter()

FOLDERS = []


@dataclass
class Folder:
    """Folder dataclass."""

    folder_id: int
    name: str


def load_folders():
    """Load folders from database."""
    global FOLDERS
    FOLDERS.append(Folder(folder_id=1, name="test"))
    return FOLDERS


@router.get("")
def list_folders():
    """List folders."""
    return FOLDERS


@router.get("/{id}")
def get_folder(id: int):
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
    files = os.listdir("./data/" + folder.name)
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
        with open("./data/" + folder.name + "/" + file.filename, "wb") as new_file:
            new_file.write(file.file.read())

    return {"filenames": [file.filename for file in files]}


@router.get("/{id}/download/{filename}")
async def download_file(id: int, filename: str):
    """Download a file from folder."""
    folder = get_folder(id)
    if not folder:
        return {"error": "folder not found."}
    return FileResponse(
        path="./data/" + folder.name + "/" + filename,
        filename=filename,
        media_type="application/octet-stream",
    )
