import pandas as pd
import sqlite3

from rapp.parser import RappConfigParser
from rapp.pipeline import MLPipeline


if __name__ == "__main__":
    parser = RappConfigParser()
    args = parser.parse_args()

    con = sqlite3.connect(args.filename)
    with open(args.sql_filename) as f:
        sql_query = f.readlines()
        sql_query = ''.join(sql_query)
    args.sql_df = pd.read_sql_query(sql_query, con)

    MLPipeline(args)
