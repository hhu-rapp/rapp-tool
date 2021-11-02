# RAPP_Prediction library

# standard library
import sqlite3
import os

# common
import pandas as pd
import sklearn as sk

# Metrics
# Classification
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
# Regression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score


# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold

import rapp.models as models

# evaluation report
from sklearn.metrics import classification_report
from sklearn.metrics import plot_confusion_matrix

# plots
import matplotlib.pyplot as plt

# tools
from sklearn.model_selection import train_test_split


class MLPipeline(object):

    def __init__(self, args):
        self.args = args

        self.args.plot_confusion_matrix = eval(self.args.plot_confusion_matrix)
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

        # hyperparameter tuning, boosting, bagging
        self.tune_estimators()

        if self.args.type == 'classification':
            self.used_scores = {
                'Accuracy': accuracy_score,
                'Balanced Accuracy': balanced_accuracy_score,
                'F1': lambda x, y: f1_score(x, y, average='macro'),
                'Recall': lambda x, y: recall_score(x, y, average='macro'),
                'Precision': lambda x, y: precision_score(x, y, average='macro'),
                'Area under ROC': roc_auc_score,
            }
        else:
            self.used_scores = {
                'Mean Absolute Error': mean_absolute_error,
                'Mean Squared Error': mean_squared_error,
                'R2': r2_score,
            }

        self.scores = {}
        for est in self.estimators:
            self.scores[est] = {}
            for sc_name in self.used_scores.keys():
                self.scores[est][sc_name] = None

        self.score_estimators()

        # Report results
        self.report_dict, self.report_df = self.create_report()
        self.print_report(self.report_df)
        if self.args.save_report:
            self.save_report(self.report_df)

        # visualize results
        if self.args.type == 'classification' and self.args.plot_confusion_matrix:
            self.plot_confusion_matrix()

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

    def score_estimators(self):

        for est in self.estimators:
            y_pred = est.predict(self.X_val)
            for sc_name, sc_fun in self.used_scores.items():
                self.scores[est][sc_name] = sc_fun(self.y_val, y_pred)


    def tune_estimators(self):
        pass

    def create_report(self):
        """
        Returns
        -------
        dict
            Dictionary of classifiers with dictionaries of evaluation metrics
            {'classifier1': {'precision':0.5,
                'recall':1.0,
                'f1-score':0.67,
                'support':1},
              'classifier2': { ... },
               ...
            }
        """
        report_dict = self.scores

        return report_dict, pd.DataFrame.from_dict(report_dict)

    def print_report(self, report_df):
        """
        Prints the report dataframe

        Parameters
        ----------
        report_df: dataframe

        Returns
        -------
        prints self.report_dict
        """
        print(report_df)

    def save_report(self, report_df):
        """
        Parameters
        ----------
        report_df: dataframe

        Returns
        -------
        dict
            Dictionary of classifiers with dictionaries of evaluation metrics
            {'classifier1': {'precision':0.5,
                'recall':1.0,
                'f1-score':0.67,
                'support':1},
              'classifier2': { ... },
               ...
            }
        """
        filename = 'results_report.csv'
        if len(self.args.report_path) > 0:
            # create directory if it does not exist
            if not os.path.exists(self.args.report_path):
                os.makedirs(self.args.report_path)

            # export file
            report_df.to_csv(self.args.report_path+'/'+filename, index=True)
        elif self.args.save_report:
            report_df.to_csv(filename, index=True)

    def plot_confusion_matrix(self):
        for i in range(len(self.estimators)):
            plot_confusion_matrix(self.estimators[i], self.X_val, self.y_val,
                                  cmap=plt.cm.Blues)
            plt.title(str(self.estimators[i]))

        plt.show()
