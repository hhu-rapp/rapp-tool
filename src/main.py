# RAPP_Prediction library

# standard library
import sqlite3
import argparse

# machine learning
import numpy as np
import sklearn as sk
# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold
# tools
from sklearn.model_selection import train_test_split
import pandas as pd


class MLPipeline(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser()

        # parsing arguments
        self.parser.add_argument("-f", "--filename", type=str, help="Location of the .db file.")
        self.parser.add_argument("-s", "--sql_filename", type=str, help="Location of the sql "
                                                                        "query file.")
        self.parser.add_argument("-l", "--label_name", type=str, help="Column name of the prediction label.")
        self.parser.add_argument("-c", "--categorical", type=str, help="List of categorical columns.",
                                 default="auto")

        self.args = self.parser.parse_args()

        # reading and quering database
        con = sqlite3.connect(self.args.filename)
        with open(self.args.sql_filename) as f:
            sql_query = f.readlines()
        self.df = pd.read_sql_query(sql_query, con)

        # create data
        self.X = self.df.drop(self.args.label_name, axis=1, inplace=False)
        self.y = self.df[self.args.label_name]

        # fill missing values
        self.impute()

        # transform data, normalization
        self.transform()

        # feature selection, dimensionality reduction
        self.feature_selection()

        # split dataset
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(self.X, self.y,
                                                                              train_size=0.8, random_state=42)

        self.train_estimators()
        self.tune_estimators()
        self.validate_estimators()
        self.save_report()

    def impute(self, method="iterative"):
        if method == "knn":
            imputer = KNNImputer(n_neighbors=5, weights="distance")
        elif method == "iterative":
            imputer = IterativeImputer()
        elif method == "mean":
            imputer = SimpleImputer(strategy="mean")
        elif method == "median":
            imputer = SimpleImputer(strategy="median")
        elif method == "most_frequent":
            imputer = SimpleImputer(strategy="most_frequent")
        else:
            imputer = KNNImputer(n_neighbors=5, weights="distance")

        self.X = imputer.fit_transform(self.X)

    def transform(self):
        """
        Transforms categorical columns to multiple columns (one-hot)

        Returns
        -------
        None
        """

        if self.args.categorical == "auto":
            pass
        else:
            list_cat_cols = eval(self.args.categorical)
            self.X = pd.get_dummies(data=self.X, columns=list_cat_cols)

    def feature_selection(self, method="variance"):
        """
        Selects the most important features based on the used strategy

        Returns
        -------
        None
        """

        if method == "variance":
            sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
            self.X = sel.fit_transform(self.X)
        else:
            sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
            self.X = sel.fit_transform(self.X)

    def train_estimators(self):
        pass

    def validate_estimators(self):
        pass

    def tune_estimators(self):
        pass

    def save_report(self):
        pass


if __name__ == '__main__':
    MLPipeline()
