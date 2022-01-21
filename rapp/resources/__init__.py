import importlib.resources as rc


def get_text(resource: str):
    return rc.read_text('rapp.resources', resource)


def get_path(resource_name: str):
    return rc.path('rapp.resources', resource_name)
