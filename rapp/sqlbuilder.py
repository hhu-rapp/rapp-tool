"""
Allows the building of quick SQL queries by giving only the
desired features id and label id.

It is assumed, that the features and labels are stored under the directories
called `sqltemplates/features` and `sqltemplates/labels`, respectively.
"""
import os
from os import path

import chevron

__TEMPLATEDIR = path.join(os.getcwd(), 'sqltemplates')


def load_sql(features_id, labels_id):
    f_select, f_join, f_where = __load_components("features", features_id)
    l_select, l_join, l_where = __load_components("labels", labels_id)

    templates_path = path.join(__TEMPLATEDIR, 'basetemplate.sql')
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


def __load_components(type, id):
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
    template_path = path.join(__TEMPLATEDIR, type, id)

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


def list_available_features():
    """
    List all available features.
    """
    dir = path.join(__TEMPLATEDIR, 'features')
    return sorted(__list_subdirs(dir))


def list_available_labels():
    """
    List all available labels.
    """
    dir = path.join(__TEMPLATEDIR, 'labels')
    return sorted(__list_subdirs(dir))


def __list_subdirs(directory: str):
    with os.scandir(directory) as it:
        return [d.name for d in it if d.is_dir()]
