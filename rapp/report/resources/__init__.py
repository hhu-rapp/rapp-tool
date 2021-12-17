import importlib.resources as rc


def get_text(resource: str):
    return rc.read_text('rapp.report.resources', resource)


def get_path(resource_name: str):
    return rc.path('rapp.report.resources', resource_name)
