"""Plugin loading."""
import inspect
import json
import logging
import os
import pkgutil
from typing import Any

import jinja2


class Plugin:
    """Basemodel for plugins."""

    input_model = None
    output_model = None
    arguments = input_model

    def __init__(self, arguments: str, variables):
        """Init."""

        if arguments:
            environment = jinja2.Environment()

            template = environment.from_string(arguments)
            tmp = {}
            for var in variables:
                tmp[var] = json.dumps(variables[var])
            arguments = template.render(**tmp)

        if not self.input_model:
            self.arguments = json.loads(arguments)
        else:
            self.arguments = self.input_model(**json.loads(arguments))
        self.variables = variables

    def process(self):
        """Run plugin process."""
        ...

    def set_variable(self, name: str, value):
        """Set a variable."""
        self.variables[name] = value

    def get_variable(self, name) -> Any:
        """Get a variable."""
        if name in self.variables:
            return self.variables[name]
        return None


def split_uppercase(in_str: str):
    """Split uppercase name with _."""
    res = ""
    for i in in_str:
        if i.isupper():
            res += "_" + i
        else:
            res += i
    return res.strip("_")


class PluginCollection:
    """Loads plugins."""

    def __init__(self, plugin_package):
        """Init the loading of available plugins."""
        self.plugin_package = plugin_package
        self.reload_plugins()

    def reload_plugins(self):
        """Reset the list of all plugins and reloads the plugins."""
        self.plugins = []
        self.seen_paths = []
        self.walk_package(self.plugin_package)

    async def run_plugins_on_event(self, event, event_data):
        """Apply all of the plugins on the argument supplied to this function."""
        status = False
        available = False
        for plugin in self.plugins:
            tmp_status = plugin.check_operation(event, event_data)
            if tmp_status:
                available = True
                break
        if not available:
            logging.info('event "%s" is not for me.', event)
            return False
        for plugin in self.plugins:
            if plugin.check_operation(event, event_data):
                logging.info('running event "%s"', event)
                status = await plugin.perform_operation(event, event_data)
                logging.info('event "%s" is done', event)
                if status:
                    return True
        return False

    def walk_package(self, package):
        """Recursively walk the supplied package to retrieve all plugins."""
        imported_package = __import__(package, fromlist=["blah"])

        for _, pluginname, ispkg in pkgutil.iter_modules(
            imported_package.__path__, imported_package.__name__ + "."
        ):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=["blah"])
                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
                for _, clsmember in clsmembers:
                    # Only add classes that are a sub class of Plugin, but NOT Plugin itself
                    if issubclass(clsmember, Plugin) & (clsmember is not Plugin):
                        clsmember.name = (  # type: ignore
                            str(clsmember.__module__).split(".")[-1].lower()
                            + "_"
                            + split_uppercase(str(clsmember.__name__)).lower()
                        )
                        self.plugins.append(clsmember)

        # Now that we have looked at all the modules in the current package, start looking
        # recursively for additional modules in sub packages
        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])

        for pkg_path in all_current_paths:
            if pkg_path not in self.seen_paths:
                self.seen_paths.append(pkg_path)

                # Get all sub directory of the current package path directory
                child_pkgs = [
                    p
                    for p in os.listdir(pkg_path)
                    if os.path.isdir(os.path.join(pkg_path, p))
                ]

                # For each sub directory, apply the walk_package method recursively
                for child_pkg in child_pkgs:
                    self.walk_package(package + "." + child_pkg)
