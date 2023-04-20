"""Plugins."""
from __future__ import annotations

from fastapi import APIRouter

from filetransferautomation.plugin_collection import PluginCollection

router = APIRouter()


@router.get("")
def get_plugins():
    """Get all plugins."""
    plugins = []
    step_plugins = PluginCollection("filetransferautomation.step_plugins")
    for plugin in step_plugins.plugins:
        plugins.append(
            {
                "name": plugin.name,
                "description": plugin.__doc__,
                "input_model": plugin.input_model.schema(),
                "output_model": plugin.output_model.schema(),
            }
        )
    return plugins
