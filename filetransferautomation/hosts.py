"""Hosts data."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, shemas
from filetransferautomation.database import SessionLocal
from filetransferautomation.models import Host

router = APIRouter()


def get_host(host_id: int) -> models.Host | None:
    """Get a host."""
    db = SessionLocal()
    db_host = db.query(models.Host).filter(models.Host.host_id == host_id).one_or_none()
    if not db_host:
        raise HTTPException(status_code=404, detail="host not found")
    return db_host


@router.get("")
async def get_hosts():
    """Get all hosts."""
    db = SessionLocal()
    result = db.query(models.Host).all()
    return result


@router.post("", status_code=201)
async def add_host(host: shemas.AddHost):
    """Add a host."""
    db = SessionLocal()
    db_host = Host(**host.dict())
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host


@router.put("/{host_id}")
async def update_host(host_id: int, host: shemas.AddHost):
    """Update a host."""
    db = SessionLocal()
    db_host = db.query(Host).filter(Host.host_id == host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="host not found")
    if db_host:
        db_host.update(dict(host))
        db.commit()
        db_host = db.query(Host).filter(Host.host_id == host_id).one_or_none()
        return db_host
    return None


@router.delete("/{host_id}", status_code=204)
async def delete_host(host_id: int):
    """Delete a host."""
    db = SessionLocal()
    db_host = db.query(Host).filter(Host.host_id == host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="host not found")
    if db_host:
        db_host.delete()
        db.commit()
    return None
