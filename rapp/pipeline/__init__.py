import sqlite3
import pandas as pd

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
from rapp.pipeline import training


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

        self.prepare_datasets()

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

        # Create a dictionary yielding possibly additionally trained models
        # for each classifier. List of additional models can be empty.
        self.additional_models = \
            dict(map(lambda clf: (clf, []), self.estimators, ))

        report = ClassifierReport(self.estimators, self.args)

        report_data = report.calculate_reports(
            self.X_train, self.y_train, self.Z_train, self.X_test, self.y_test, self.Z_test)

        report.write_report(report_data)

    def calc_sensitive_attributes(self, X_data):
        cols = []
        for i, sensitive in self.args.sensitive_attributes.enumerate():
            if sensitive in self.args.categorical:
                col_name = sensitive + '_' + self.args.privileged_groups[i]

    def get_estimators(self):
        return self.estimators

    def impute(self, method='iterative'):
        # Only impute categorical data
        if self.args.categorical != []:
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

    def prepare_datasets(self):
        # create data
        self.X = self.df.drop(self.args.label_name, axis=1, inplace=False)
        self.y = self.df[self.args.label_name]

        # Adapt to categorical data.
        columns = [x for x in self.args.categorical if x !=
                   self.args.label_name]
        categorical = pd.get_dummies(data=self.X[columns], columns=columns)
        self.X = pd.concat([self.X, categorical], axis=1)
        # For now we kept the original version. This is due to it maybe being a
        # sensitive attribute as well. These need to be treated differently.
        # We will fix this below after the train_test_split as to not lose the
        # relation between sensitive attributes and individuals.

        # feature selection, dimensionality reduction
        # self.feature_selection(self.args.feature_selection)

        # split datasets
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y,
                                                                                train_size=0.8, random_state=42)

        # Save protected attribute
        self.Z_train = self.X_train[self.args.sensitive_attributes]
        self.Z_test = self.X_test[self.args.sensitive_attributes]
        # Remove categorical attributes from input features
        self.X_train = self.X_train.drop(columns, axis=1)
        self.X_test = self.X_test.drop(columns, axis=1)

        # TODO: Unawareness. If user so desires, drop all info of sensitive attributes.

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
        for est in self.estimators:
            est.fit(self.X_train, self.y_train)

            training.get_additional_models(
                est, self.X_train, self.y_train, self.X_test, self.y_test)
