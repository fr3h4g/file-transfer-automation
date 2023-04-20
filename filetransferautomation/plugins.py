"""Plugins."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from filetransferautomation import models, shemas
from filetransferautomation.database import SessionLocal
from filetransferautomation.models import Schedule
from filetransferautomation.plugin_collection import PluginCollection

router = APIRouter()


@router.get("")
def get_plugins():
    """Get all plugins."""
    plugins = []
    step_plugins = PluginCollection("filetransferautomation.step_plugins")
    for plugin in step_plugins.plugins:
        plugins.append(
            {"name": plugin.name, "input_model": plugin.input_model.schema()}
        )
    return plugins
