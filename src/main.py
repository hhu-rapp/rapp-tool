# RAPP_Prediction library

# standard library
import sqlite3

# common
import numpy as np
import pandas as pd
import sklearn as sk

# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold

# ML classifiers
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

# ML regression methods
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import BayesianRidge

# tools
from sklearn.model_selection import train_test_split
import configargparse


class MLPipeline(object):

    def __init__(self):
        self.parser = configargparse.ArgParser()
        self.parser.add('-cf', '--config-file', required=True, is_config_file=True, help='config file path')

        # parsing arguments from the config file
        self.parser.add_argument("-f", "--filename", type=str, help="Location of the .db file.",
                                 required=True)
        self.parser.add_argument("-s", "--sql_filename", type=str, help="Location of the sql query file.",
                                 required=True)
        self.parser.add_argument("-l", "--label_name", type=str, help="Column name of the prediction label.",
                                 required=True)
        self.parser.add_argument("-c", "--categorical", nargs='+', help="List of categorical columns.",
                                 required=True)
        self.parser.add_argument("-t", "--type", type=str, default='classification',
                                 help="classification or regression. Default: classification",
                                 required=True)
        self.parser.add_argument("--imputation", type=str, default='iterative',
                                 help="Imputation method for non-categorical data. Available: knn, iterative, mean, "
                                      "median, most_frequent",
                                 required=False)
        self.parser.add_argument("--feature_selection", type=str, default='variance',
                                 help="Feature selection method to reduce the amount of features. Available: variance, "
                                      "",
                                 required=False)

        self.args = self.parser.parse_args()

        # reading and quering database
        con = sqlite3.connect(self.args.filename)
        with open(self.args.sql_filename) as f:
            sql_query = f.readlines()
            sql_query = "".join(sql_query)
        self.df = pd.read_sql_query(sql_query, con)

        # fill missing values
        self.impute(self.args.imputation)

        # delete label from categorical if it is contained
        self.args.categorical = [x for x in self.args.categorical if x != self.args.label_name]

        # create data
        self.X = self.df.drop(self.args.label_name, axis=1, inplace=False)
        self.y = self.df[self.args.label_name]

        # transform data, normalization
        self.transform()

        # feature selection, dimensionality reduction
        self.feature_selection(self.args.feature_selection)

        # split datasets
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(self.X, self.y,
                                                                              train_size=0.8, random_state=42)

        # create estimators & train
        if self.args.type == 'classification':
            self.estimators = [RandomForestClassifier(), SVC(), GaussianNB(), LogisticRegression()]
        else:
            self.estimators = [LinearRegression(), ElasticNet(), BayesianRidge()]
        self.train_estimators()

        # hyperparameter tuning, boosting, bagging
        self.tune_estimators()

        if self.args.type == 'classification':
            self.scores = {'accuracy': [], 'f1': [], 'recall': [], 'precision': []}
        else:
            self.scores = {'mae': [], 'r2': [], 'mse': []}
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
        # most common class as the positive label to use for metrics
        pos_label = self.df[self.args.label_name].value_counts()[:1].index.tolist()[0]

        if self.args.type == 'classification':
            for i in range(len(self.estimators)):
                y_pred = self.estimators[i].predict(self.X_val)
                self.scores['accuracy'].append(sk.metrics.accuracy_score(self.y_val, y_pred))
                self.scores['f1'].append(sk.metrics.f1_score(self.y_val, y_pred, pos_label=pos_label))
                self.scores['recall'].append(sk.metrics.recall_score(self.y_val, y_pred, pos_label=pos_label))
                self.scores['precision'].append(sk.metrics.precision_score(self.y_val, y_pred, pos_label=pos_label))
        else:
            for i in range(len(self.estimators)):
                y_pred = self.estimators[i].predict(self.X_val)
                self.scores['mae'].append(sk.metrics.mean_absolute_error(self.y_val, y_pred))
                self.scores['mse'].append(sk.metrics.mean_squared_error(self.y_val, y_pred))
                self.scores['r2'].append(sk.metrics.r2_score(self.y_val, y_pred))

    def tune_estimators(self):
        pass

    def pretty_print(self):
        # iterate through metrics
        for key_score in self.scores.keys():
            print(key_score+':')
            for i in range(len(self.estimators)):
                print('{0}: {1}'.format(self.estimators[i], self.scores[key_score][i]))

            print('')

    def save_report(self):
        pass


if __name__ == '__main__':
    MLPipeline()
