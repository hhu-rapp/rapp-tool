# internal Python packages
import os
from datetime import datetime
import argparse
import configargparse
import sqlite3

# rapp
from rapp.pipeline import MLPipeline
from rapp.parser import parse_rapp_args

# data analysis
import numpy as np
import pandas as pd
import sklearn as sk
import oapackage

# imputation
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import KNNImputer, IterativeImputer, SimpleImputer
from sklearn.feature_selection import VarianceThreshold

# ML classifiers
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

# ML regression methods
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import BayesianRidge

# evaluation report
from sklearn.metrics import classification_report
from sklearn.metrics import plot_confusion_matrix

# plots
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
# plt.rcParams['figure.figsize'] = [60, 20]

# tools
from sklearn.model_selection import train_test_split

db_filepath = "data/rapp.db"


class Explain(object):

    def __init__(self):
        self.parser = configargparse.ArgParser()
        self.parser.add('-cf', '--config-file', required=True, is_config_file=True, help='config file path')

        # parsing arguments from the config file
        self.parser = parse_rapp_args(self.parser)
        self.args = self.parser.parse_args()

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

        # delete label from categorical if it is contained
        self.args.categorical = [x for x in self.args.categorical if x != self.args.label_name]

        # create data
        self.X = self.df.drop(self.args.label_name, axis=1, inplace=False)
        self.y = self.df[self.args.label_name]

        # transform data, normalization
        self.transform()

        # split datasets
        self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(self.X, self.y,
                                                                              train_size=0.8, random_state=42)

        # create estimators & train
        if self.args.type == 'classification':
            self.estimators = [DecisionTreeClassifier(class_weight='balanced')]
        elif self.args.type == 'regression':
            self.estimators = [LinearRegression(), ElasticNet(), BayesianRidge()]
        self.train_estimators()

        # hyperparameter tuning, boosting, bagging
        self.tune_estimators()

        if self.args.type == 'classification':
            self.scores = {'Accuracy': [], 'F1': [], 'Recall': [], 'Precision': []}
        else:
            self.scores = {'Mean Absolute Error': [], 'Mean Squared Error': [], 'R2': []}
        self.score_estimators()

        # Report results
        self.report_dict, self.report_df = self.create_report()
        self.print_report(self.report_df)
        if self.args.save_report:
            self.save_report(self.report_df)

        # visualize results
        if self.args.type == 'classification' and self.args.plot_confusion_matrix:
            self.plot_confusion_matrix()

    def impute(self, method='iterative'):
        # Only impute categorical data
        self.df[self.args.categorical] = \
            SimpleImputer(strategy='most_frequent').fit_transform(self.df[self.args.categorical])

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
        self.X = pd.get_dummies(data=self.X, columns=self.args.categorical)

    def train_estimators(self):
        for i in range(len(self.estimators)):
            self.estimators[i].fit(self.X_train, self.y_train)

    def score_estimators(self):
        # most common class as the positive label to use for metrics
        pos_label = self.df[self.args.label_name].value_counts()[:1].index.tolist()[0]

        if self.args.type == 'classification':
            for i in range(len(self.estimators)):
                y_pred = self.estimators[i].predict(self.X_val)
                self.scores['Accuracy'].append(sk.metrics.accuracy_score(self.y_val, y_pred))
                self.scores['F1'].append(sk.metrics.f1_score(self.y_val, y_pred, average='macro'))
                self.scores['Recall'].append(sk.metrics.recall_score(self.y_val, y_pred, average='macro'))
                self.scores['Precision'].append(sk.metrics.precision_score(self.y_val, y_pred, average='macro'))
        elif self.args.type == 'regression':
            for i in range(len(self.estimators)):
                y_pred = self.estimators[i].predict(self.X_val)
                self.scores['Mean Absolute Error'].append(sk.metrics.mean_absolute_error(self.y_val, y_pred))
                self.scores['Mean Squared Error'].append(sk.metrics.mean_squared_error(self.y_val, y_pred))
                self.scores['R2'].append(sk.metrics.r2_score(self.y_val, y_pred))

    def tune_estimators(self):
        # getting hyperparameter space
        ccp_alphas = self.estimators[0].cost_complexity_pruning_path(self.X_train, self.y_train).ccp_alphas

        # testing hyperparameter
        clfs = []
        for ccp_alpha in ccp_alphas:
            clf = DecisionTreeClassifier(random_state=0, ccp_alpha=ccp_alpha,
                                         class_weight="balanced", min_impurity_decrease=0.001)
            clf.fit(self.X_train, self.y_train)
            clfs.append(clf)

        acc_scores = [sk.metrics.balanced_accuracy_score(self.y_val, clf.predict(self.X_val)) for clf in clfs]

        # find pareto optima
        datapoints = np.array([ccp_alphas, acc_scores]).T

        plt.scatter(datapoints[0,:], datapoints[1,:])
        plt.show()

        pareto = oapackage.ParetoDoubleLong()
        for ii in range(0, datapoints.shape[1]):
            w = oapackage.doubleVector((datapoints[0, ii], datapoints[1, ii]))
            pareto.addvalue(w, ii)

        # list of indexes of pareto optimal solutions
        lst = pareto.allindices()

        # train with selected hyperparameter
        selected_ccp = datapoints[0, lst][0]
        clf = DecisionTreeClassifier(random_state=0, class_weight="balanced", min_impurity_decrease=0.001,
                               ccp_alpha=selected_ccp)

        clf.fit(self.X_train, self.y_train)

        # save estimator into estimators
        self.estimators = [clf]

        plot_tree(clf, feature_names=self.X_train.columns, class_names=["nein", "ja"])
        plt.show()
        print('test')

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
        report_dict = {}
        for i in range(len(self.estimators)):
            cur_metrics_dict = {}
            for key_score in self.scores.keys():
                cur_metrics_dict[key_score] = self.scores[key_score][i]

            # add metrics to each classifier
            report_dict[str(self.estimators[i])] = cur_metrics_dict

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


if __name__ == '__main__':
    Explain()
