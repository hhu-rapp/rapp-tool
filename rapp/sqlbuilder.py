"""
Allows the building of quick SQL queries by giving only the
desired features id and label id.

It is assumed, that the features and labels are stored under the directories
called `sqltemplates/features` and `sqltemplates/labels`, respectively.
"""
import os
from os import path

import chevron

_DEFAULTTEMPLATEDIR = path.join(os.getcwd(), 'sqltemplates')

def load_sql(features_id, labels_id, template_dir=None):
    if template_dir is None:
        template_dir = _DEFAULTTEMPLATEDIR

    f_select, f_join, f_where = __load_components(
        "features", features_id, template_dir=template_dir)
    l_select, l_join, l_where = __load_components(
        "labels", labels_id, template_dir=template_dir)

    templates_path = path.join(template_dir, 'basetemplate.sql')
    template = __load_text(templates_path)
    mustache = {
        "feature_select": f_select,
        "feature_join": f_join,
        "feature_where": f_where,
        "label_select": l_select,
        "label_join": l_join,
        "label_where": l_where,
    }
    query = chevron.render(template, mustache)

    return query


def __load_components(type, id, template_dir=None):
    """
    For the given type and identifier,
    load the contents of the SELECT, the JOIN, and the WHERE statements.
    If no JOIN or WHERE statements exist, empty SQL statements are returned.

    Returns
    -------
    select: str
        Contents for the SELECT statement.

    join: str
        Contents for the JOIN statement.

    where: str
        Contents for the WHERE statement.
    """
    if template_dir is None:
        template_dir = _DEFAULTTEMPLATEDIR
    template_path = path.join(template_dir, type, id)

    sel_sql = path.join(template_path, "select.sql")
    sel_sql = __load_text(sel_sql)
    join_sql = path.join(template_path, "join.sql")
    join_sql = __load_sql_if_exists(join_sql)
    where_sql = path.join(template_path, "where.sql")
    where_sql = __load_sql_if_exists(where_sql)

    return sel_sql.strip(), join_sql.strip(), where_sql.strip()


def __load_sql_if_exists(resource_path):
    try:
        sql = __load_text(resource_path)
    except FileNotFoundError:
        sql = ""
    return sql


def __load_text(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def list_available_features(template_dir=None):
    """
    List all available features.
    """
    if template_dir is None:
        template_dir = _DEFAULTTEMPLATEDIR

    dir = path.join(template_dir, 'features')
    return sorted(__list_subdirs(dir))


def list_available_labels(template_dir=None):
    """
    List all available labels.
    """
    if template_dir is None:
        template_dir = _DEFAULTTEMPLATEDIR

    dir = path.join(template_dir, 'labels')
    return sorted(__list_subdirs(dir))


def __list_subdirs(directory: str):
    with os.scandir(directory) as it:
        return [d.name for d in it if d.is_dir()]
