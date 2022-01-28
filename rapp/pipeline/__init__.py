from datetime import datetime

import pandas as pd
import os

import joblib

import logging as log

# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold

import rapp.models as models

# tools
from sklearn.model_selection import train_test_split

from rapp.report import ClassifierReport
from rapp.pipeline import training

from datetime import datetime


class MLPipeline(object):

    def __init__(self, args):
        self.args = args

        self.args.save_report = self.args.save_report

        if self.args.report_path is None:
            date_path = datetime.now().strftime("%Y/%m/%d/")
            self.args.report_path = f"reports/{date_path}/{self.args.studies_id}/{self.args.labels_id}/{self.args.features_id}/"

        self.df = self.args.sql_df

        if self.args.label_name is None:
            self.label_name = self.df.columns[-1]
        else:
            self.label_name = self.args.label_name

        # fill missing values
        self.impute(self.args.imputation)

        self.prepare_datasets()

        # create estimators & train
        if self.args.classifier is not None:
            if not isinstance(self.args.classifier, list):
                self.args.classifier = [self.args.classifier]

            self.estimators = []

            for estimator in self.args.classifier:
                self.estimators.append(models.get(estimator))
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

        log.info("Training estimators")
        self.train_estimators()
        self.train_additional_models()
        log.info("Finish training of estimators")

        feature_names = list(self.X_train.columns)
        class_names = sorted(self.y_train.unique())
        if len(class_names) == 2:
            class_names = ["Nein", "Ja"]

        report = ClassifierReport(
            self.estimators, self.args, self.additional_models,
            feature_names=feature_names, class_names=class_names)

        report_data = report.calculate_reports(
            self.X_train, self.y_train, self.Z_train, self.X_test, self.y_test, self.Z_test)

        log.debug("Writing report to path '%s'", self.args.report_path)
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
        self.X = self.df.drop(self.label_name, axis=1, inplace=False)
        self.y = self.df[self.label_name]

        # Adapt to categorical data.
        columns = [x for x in self.args.categorical if x !=
                   self.label_name]
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

            # Save model
            target_path = os.path.join(
                self.args.report_path,  est.__class__.__name__)
            os.makedirs(target_path, exist_ok=True)
            model_path = os.path.join(target_path, "model.joblib")

            joblib.dump(est, model_path)

    def train_additional_models(self):
        # Create a dictionary yielding possibly additionally trained models
        # for each classifier. List of additional models can be empty.
        self.additional_models = \
            dict(map(lambda clf: (clf, []), self.estimators, ))

        for est in self.estimators:
            self.additional_models[est] = \
                training.get_additional_models(
                    est, self.X_train, self.y_train, self.X_test, self.y_test)

            # Save the models
            id = 0
            for m in self.additional_models[est]:
                m["id"] = id

                save = m.get('save_model', True)
                if save:
                    model = m["model"]
                    rel_path = os.path.join(est.__class__.__name__,
                                            "additional_models",
                                            f"{id}.joblib")
                    path = os.path.join(self.args.report_path, rel_path)
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    joblib.dump(model, path)
                    m["save_path"] = {"full": path, "relative": rel_path}
                id += 1  # Update id for next run
