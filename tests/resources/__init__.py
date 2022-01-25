import os
import pkgutil
import sys

import sqlite3


def get_text(resource: str):
    rc = pkgutil.get_data('tests.resources', resource).decode()
    return rc


def get_data(resource: str):
    rc = pkgutil.get_data('tests.resources', resource)
    return rc


def get_path(resource: str):
    # Adapted from https://stackoverflow.com/a/13773912
    package = 'tests.resources'
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


def get_db_connection():
    """
    Returns: Connection to a memory database which contains the
    entries of `test.db`.

    Altering the values in the returned connection has no effect onto the
    data of the test.db.
    """
    path = get_path('test.db')
    # Open test db, then copy/backup contents to memory db.
    test_db = sqlite3.connect(path)
    mem_db = sqlite3.connect(":memory:")
    test_db.backup(mem_db)
    return mem_db
