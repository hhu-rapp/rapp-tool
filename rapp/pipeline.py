# RAPP_Prediction library

import sqlite3
import pandas as pd

import pprint

# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold

import rapp.models as models

# plots
import matplotlib.pyplot as plt

# tools
from sklearn.model_selection import train_test_split

from rapp.report import ClassifierReport



class MLPipeline(object):

    def __init__(self, args):
        self.args = args

        self.args.save_report = eval(self.args.save_report)

        # reading and quering database
        con = sqlite3.connect(self.args.filename)
        with open(self.args.sql_filename) as f:
            sql_query = f.readlines()
            sql_query = ''.join(sql_query)
        self.df = pd.read_sql_query(sql_query, con)

        # fill missing values
        self.impute(self.args.imputation)

        # create data
        self.X = self.df.drop(self.args.label_name, axis=1, inplace=False)
        self.y = self.df[self.args.label_name]

        # transform data, normalization
        self.transform()

        # feature selection, dimensionality reduction
        # self.feature_selection(self.args.feature_selection)

        # split datasets
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(self.X, self.y,
                                                                              train_size=0.8, random_state=42)

        # create estimators & train
        if self.args.classifier is not None:
            self.estimators = [models.get(self.args.classifier)]
            self.train_estimators()
        else:
            if self.args.type == 'classification':
                self.estimators = [
                    models.get('RF'),
                    models.get('DT'),
                    models.get('SVM'),
                    models.get('NB'),
                    models.get('LR'),
                ]
            elif self.args.type == 'regression':
                self.estimators = [
                    models.get_regressor('LR'),
                    models.get_regressor('EL'),
                    models.get_regressor('BR'),
                ]
            self.train_estimators()


        report = ClassifierReport(self.estimators, self.args)
        report_data = report.calculate_reports(self.X_train, self.y_train, self.X_val, self.y_val)
        pp = pprint.PrettyPrinter()
        pp.pprint(report_data)


    def get_estimators(self):
        return self.estimators

    def impute(self, method='iterative'):
        # Only impute categorical data
        self.df[self.args.categorical] = \
            SimpleImputer(strategy='most_frequent').fit_transform(
                self.df[self.args.categorical])

        # impute non-categorical data
        if method == 'knn':
            imputer = KNNImputer(n_neighbors=5, weights='distance')
        elif method == 'iterative':
            imputer = IterativeImputer()
        elif method == 'mean':
            imputer = SimpleImputer(strategy='mean')
        elif method == 'median':
            imputer = SimpleImputer(strategy='median')
        elif method == 'most_frequent':
            imputer = SimpleImputer(strategy='most_frequent')
        else:
            imputer = KNNImputer(n_neighbors=5, weights='distance')

        self.df[self.df.columns.difference(self.args.categorical)] \
            = imputer.fit_transform(self.df[self.df.columns.difference(self.args.categorical)])

    def transform(self):
        """
        Transforms categorical columns to multiple columns (one-hot)

        Returns
        -------
        None
        """

        columns = [x for x in self.args.categorical if x != self.args.label_name]
        self.X = pd.get_dummies(data=self.X, columns=columns)



    def feature_selection(self, method='variance'):
        """
        Selects the most important features based on the used strategy

        Returns
        -------
        None
        """

        if method == 'variance':
            sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
            self.X = sel.fit_transform(self.X)
        else:
            sel = VarianceThreshold(threshold=(.8 * (1 - .8)))
            self.X = sel.fit_transform(self.X)


    def train_estimators(self):
        for i in range(len(self.estimators)):
            self.estimators[i].fit(self.X_train, self.y_train)
