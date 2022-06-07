import os
import pkgutil
import sys


def get_text(resource: str):
    rc = pkgutil.get_data('rapp.resources', resource).decode()
    return rc


def get_data(resource: str):
    rc = pkgutil.get_data('rapp.resources', resource)
    return rc


def get_path(resource: str):
    # Adapted from https://stackoverflow.com/a/13773912
    package = 'rapp.resources'
    loader = pkgutil.get_loader(package)
    if loader is None or not hasattr(loader, 'get_data'):
        return None
    mod = sys.modules.get(package) or loader.load_module(package)
    if mod is None or not hasattr(mod, '__file__'):
        return None

    parts = resource.split('/')
    parts.insert(0, os.path.dirname(mod.__file__))
    resource_name = os.path.join(*parts)

    return resource_name


def list_subdirs(resource: str):
    path = get_path(resource)

    with os.scandir(path) as it:
        return [d.name for d in it if d.is_dir()]
