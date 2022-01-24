
import pkgutil


def get_text(resource: str):
    rc = pkgutil.get_data('tests.resources', resource).decode()
    return rc


def get_data(resource: str):
    rc = pkgutil.get_data('tests.resources', resource)
    return rc
