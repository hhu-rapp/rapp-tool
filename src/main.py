# RAPP_Prediction library

# standard library
import sqlite3
import argparse

# common
import numpy as np
import pandas as pd

# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold

# ML classifiers
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# ML regression methods
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import BayesianRidge

# tools
from sklearn.model_selection import train_test_split


class MLPipeline(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser()

        # parsing arguments
        self.parser.add_argument("-f", "--filename", type=str, help="Location of the .db file.",
                                 required=True)
        self.parser.add_argument("-s", "--sql_filename", type=str, help="Location of the sql query file.",
                                 required=True)
        self.parser.add_argument("-l", "--label_name", type=str, help="Column name of the prediction label.",
                                 required=True)
        self.parser.add_argument("-c", "--categorical", nargs='+', help="List of categorical columns.",
                                 required=True)

        self.args = self.parser.parse_args()

        # reading and quering database
        con = sqlite3.connect(self.args.filename)
        with open(self.args.sql_filename) as f:
            sql_query = f.readlines()
            sql_query = "".join(sql_query)
        self.df = pd.read_sql_query(sql_query, con)

        # fill missing values
        self.impute()

        # create data
        self.X = self.df.drop(self.args.label_name, axis=1, inplace=False)
        self.y = self.df[self.args.label_name]

        # transform data, normalization
        self.transform()

        # feature selection, dimensionality reduction
        self.feature_selection()

        # split dataset
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(self.X, self.y,
                                                                              train_size=0.8, random_state=42)

        # create classifiers & train
        #self.estimators = [RandomForestClassifier(), SVC(), GaussianNB()]
        self.estimators = [LinearRegression(), ElasticNet(), BayesianRidge()]
        self.train_estimators()

        # hyperparameter tuning, boosting, bagging
        self.tune_estimators()

        #self.scores = {'accuracy': [], 'f1': [], 'recall': [], 'precision': []}
        self.scores = {'standard': [], 'r2': []}
        self.score_estimators()

        self.pretty_print()
        self.save_report()

    def impute(self, method="iterative"):
        # Only impute categorical data
        self.df[self.args.categorical] = \
            SimpleImputer(strategy="most_frequent").fit_transform(self.df[self.args.categorical])

        # impute non-categorical data
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

        self.df[self.df.columns.difference(self.args.categorical)] \
            = imputer.fit_transform(self.df[self.df.columns.difference(self.args.categorical)])

    def transform(self):
        """
        Transforms categorical columns to multiple columns (one-hot)

        Returns
        -------
        None
        """
        self.X = pd.get_dummies(data=self.X, columns=self.args.categorical)

    def feature_selection(self, method="variance"):
        # TODO: transforms data weirldy to another format
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
        for i in range(len(self.estimators)):
            self.estimators[i].fit(self.X_train, self.y_train)

    def score_estimators(self):
        # score_keys = self.scores.keys()
        for i in range(len(self.estimators)):
            self.scores['standard'].append(self.estimators[i].score(self.X_val, self.y_val))

    def tune_estimators(self):
        pass

    def pretty_print(self):
        for i in range(len(self.estimators)):
            print('{0}: {1}'.format(self.estimators[i], self.scores['standard'][i]))

    def save_report(self):
        pass


if __name__ == '__main__':
    MLPipeline()