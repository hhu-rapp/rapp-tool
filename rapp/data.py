"""
Unified API for accessing the database and loading SQL queries.
"""

import pandas as pd
import sqlite3

db_conn = None


def connect(db_path):
    "Connect to the specified database. Returns the connection."
    global db_conn
    db_conn = sqlite3.connect(db_path)
    return db_conn


def query_sql(sql_query, connection=db_conn):
    """
    Execute an SQL query over the given database connection.
    Return the results as pandas.DataFrame.
    """
    df = pd.read_sql_query(sql_query, connection)
    return df


def query_sql_file(sql_file, connection=db_conn):
    """
    `sql_file`: Path to an sql file.
    `connection`: database connection.
    Return the results as pandas.DataFrame.
    """
    with open(sql_file, 'r') as f:
        query = f.read()
        # Todo: do we need to escape the sql contents?
        return query_sql(query, connection)
