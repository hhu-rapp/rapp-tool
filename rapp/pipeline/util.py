import sqlite3
import pandas as pd

from rapp.parser import RappConfigParser
from rapp.pipeline import MLPipeline

def load_pipeline_from_config():
    """
    Reads the command line call and parses the arguments to run a
    `rapp.pipeline.MLPipeline` instance.

    This function incorporates boilerplate code to ease refactoring.
    """
    parser = RappConfigParser()
    args = parser.parse_args()

    con = sqlite3.connect(args.filename)
    with open(args.sql_filename) as f:
        sql_query = f.readlines()
        sql_query = ''.join(sql_query)
    args.sql_df = pd.read_sql_query(sql_query, con)

    return MLPipeline(args)
