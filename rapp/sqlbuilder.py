"""
Allows the building of quick SQL queries by giving only the
desired features id and label id.

The allowed ids are

* for features
    * cs_first_term_modules
* for labels
    * master_admission
    * 3_dropout
    * 4term_cp
    * 4term_ap
    * rsz
"""
from os import path

import chevron

import data as dt


def load_sql(features_id, labels_id, project_name="survey"):
    f_select, f_join, f_where = __load_components(project_name, "features", features_id)
    l_select, l_join, l_where = __load_components(project_name, "labels", labels_id)

    templates_path = path.join(project_name, "sqltemplates", "skeleton.sql")
    template = dt.get_text(templates_path)
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


def __load_components(project, type, id):
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
    template_path = path.join(project, "sqltemplates/", type, id)

    sel_sql = path.join(template_path, "select.sql")
    sel_sql = dt.get_text(sel_sql)
    join_sql = path.join(template_path, "join.sql")
    join_sql = __load_sql_if_exists(join_sql)
    where_sql = path.join(template_path, "where.sql")
    where_sql = __load_sql_if_exists(where_sql)

    return sel_sql.strip(), join_sql.strip(), where_sql.strip()


def __load_sql_if_exists(resource_path):
    try:
        sql = dt.get_text(resource_path)
    except FileNotFoundError:
        sql = ""
    return sql
