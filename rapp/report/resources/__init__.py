import importlib.resources as rc


def get_text(resource):
    return rc.read_text('rapp.report.resources', resource)
