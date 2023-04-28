"""Folders."""
from __future__ import annotations

import os

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

from filetransferautomation import models, settings
from filetransferautomation.database import SessionLocal
from filetransferautomation.shemas import Folder as FolderSchema

router = APIRouter()


def load_folders():
    """Load folders from database."""
    with SessionLocal() as db:
        folders = db.query(models.Folder).all()

    for folder in folders:
        path = os.path.join(settings.FOLDERS_DIR, folder.name)
        if not os.path.exists(path):
            os.makedirs(path)
    return folders


@router.get("")
def list_folders():
    """List folders."""
    with SessionLocal() as db:
        folders = db.query(models.Folder).all()
    return folders


@router.get("/{id}")
def get_folder(id: int) -> FolderSchema | None:
    """Get a folder."""
    folder = None
    with SessionLocal() as db:
        folder = (
            db.query(models.Folder).filter(models.Folder.folder_id == id).one_or_none()
        )
    return folder


@router.get("/{id}/files")
def get_files(id: int):
    """List files in folder."""
    folder = get_folder(id)
    if not folder:
        return {"details": "folder not found."}
    files = os.listdir(os.path.join(settings.FOLDERS_DIR, folder.name))
    return files


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
