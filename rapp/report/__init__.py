# Metrics
# Classification
from sklearn.metrics import accuracy_score
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
# Regression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
# Cross Validation
from sklearn.model_selection import cross_validate
from sklearn.metrics import  make_scorer

from rapp.fair.notions import clf_fairness
from rapp.fair.notions import group_fairness
from rapp.fair.notions import equality_of_opportunity
from rapp.fair.notions import predictive_equality

import os
import json
import shutil
import subprocess
import logging
import joblib

import numpy as np

from rapp.report import latex
from rapp.report import resources as rc


class ClassifierReport(object):

    def __init__(self, estimators, config_args, additional_models={},
                 feature_names=None,
                 class_names=None) -> None:
        """
        Parameters
        ----------
        estimators: list of already trained classifiers.

        config_args: Parser arguments from parser.RappConfigParser.

        additional_models : dict, optional
            Dictionary with estimators as keys. Behind each key is a list of
            {'model': trained_model, ...} dictionaries which where additionally
            trained for the key estimator.
            Lists might be empty.

        feature_names: list(str), optional
            Names of the features in order used to train the estimators.

        class_names: list(str), optional
            Names of the classes in order predicted by the estimators.
        """
        super().__init__()

        self.estimators = estimators
        self.cf_args = config_args

        self.features = feature_names
        self.classes = class_names

        # Ensure that additional_models has each estimator as key.
        for est in estimators:
            if est not in additional_models.keys():
                additional_models[est] = []

        self.additional_models = additional_models

        self.sensitive = config_args.sensitive_attributes

        self.used_scores = {
            'Accuracy': accuracy_score,
            'Balanced Accuracy': balanced_accuracy_score,
            'F1': lambda x, y: f1_score(x, y, average='macro'),
            'Recall': lambda x, y: recall_score(x, y, average='macro'),
            'Precision': lambda x, y: precision_score(x, y, average='macro'),
            'Area under ROC': lambda x, y: roc_auc_score(x, y, multi_class='ovr')
        }

        self.used_fairnesses = {
            "Statistical Parity": group_fairness,
            "Predictive Equality": predictive_equality,
            "Equality of Opportunity": equality_of_opportunity,
        }

    def calculate_reports_deprecated(self, X_train, y_train, z_train, X_test, y_test, z_test):
        reports = {}
        sets = [('train', X_train, y_train, z_train),
                ('test', X_test, y_test, z_test)]

        for (set_name, X, y, z) in sets:
            # TODO: Does it even matter for CV?
            set_rep = self.calculate_set_statistics(X, y, z)
            reports[set_name] = set_rep

        estimator_reports = {}
        for est in self.estimators:
            est_rep = {}
            for (set_name, X, y, z) in sets:
                est_rep[set_name] = self.calculate_single_set_report_deprecated(
                    est, X, y, z)
            # Also do this for any additionally trained classifiers.
            est_rep["additional_models"] = []
            for add_est in self.additional_models[est]:
                add_info = {key: add_est[key] for key in add_est
                            if key != 'model'}
                # Measure performances as well
                for (set_name, X, y, z) in sets:
                    add_info[set_name] = self.calculate_single_set_report_deprecated(
                        add_est['model'], X, y, z)
                est_rep["additional_models"].append(add_info)

            estimator_reports[self.clf_name(est)] = est_rep
        reports['estimators'] = estimator_reports

        return reports

    def calculate_reports(self, X, y, z):
        reports = {}

        set_rep = self.calculate_set_statistics(X, y, z)
        reports['Dataset'] = set_rep

        estimator_reports = {}
        for est in self.estimators:
            est_rep = {}
            est_rep['CV'] = self.calculate_single_report(est, X, y, z, cv=5)

            # Also do this for any additionally trained classifiers.
            est_rep["additional_models"] = []
            for add_est in self.additional_models[est]:
                add_info = {key: add_est[key] for key in add_est
                            if key != 'model'}
                # Measure performances as well
                add_info['CV'] = self.calculate_single_report(add_est['model'], X, y, z, save_models=False, cv=5)

                est_rep["additional_models"].append(add_info)

            estimator_reports[self.clf_name(est)] = est_rep

        reports['estimators'] = estimator_reports
        return reports


    def clf_name(self, estimator):
        return estimator.__class__.__name__

    def calculate_set_statistics(self, X, y, z):
        set_stats = {'total': len(y),
                     'outcomes': {},
                     'groups': {}}

        values = y.unique()
        for v in values:
            num = len(y[y == v])
            set_stats['outcomes'][v] = num

        for g in z.columns:
            group_stats = {}
            for gvalue in z[g].unique():
                data = y[z[g] == gvalue]
                group_stats[gvalue] = {'total': len(data),
                                       'outcomes': {}}
                for v in values:
                    num = len(data[y == v])
                    group_stats[gvalue]['outcomes'][v] = num
            set_stats['groups'][g] = group_stats

        return set_stats

    def calculate_single_report(self, estimator, X, y, z, save_models=True, **kwargs):
        scorings = {}
        cv_scores = cross_validate(estimator, X, y, scoring=self.get_score_dict(), return_estimator=True ,return_train_score=True ,**kwargs)

        est_scores = {}
        est_cf = {}
        for i, est in enumerate(cv_scores['estimator']):
            # get score dict for each estimator trained
            est_scores[i] = self.get_cv_scores(cv_scores, i)

            pred = est.predict(X)
            C = confusion_matrix(y, pred)
            est_cf[i] = C.tolist()

        scorings['scores'] = est_scores
        scorings['confusion_matrix'] = est_cf

        fairness = {}
        for group in z.columns:
            fairness[group] = {}
            for notion, fun in self.used_fairnesses.items():
                fairness[group][notion] = \
                    clf_fairness(estimator, fun, X, y, z[group], pred)
        scorings["fairness"] = fairness

        if save_models:
            self.save_estimators(cv_scores['estimator'])
        return scorings

    def get_score_dict(self):
        score_dict = {}
        for scoring_name, fun in self.used_scores.items():
            score_dict[scoring_name] = make_scorer(fun)
        return score_dict

    def get_cv_scores(self, cv_scores, index):
        score_dict = {}
        score_dict['train'] = {}
        score_dict['test'] = {}
        for score in cv_scores:
            key = score.split('_')

            if key[0] == 'train' :
                score_dict['train'][key[1]] = cv_scores[score][index]
            if key[0] == 'test' :
                score_dict['test'][key[1]] = cv_scores[score][index]

        return score_dict

    def write_report(self, report_data, path=None):
        if path is None:
            path = self.cf_args.report_path

        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            logging.error(f"Could not write report to {path}:", e)

        with open(os.path.join(path, "report.json"), 'w') as r:
            json.dump(report_data, r, indent=2)

        latex_report_file = os.path.join(path, "report.tex")
        logging.info("Writing LaTeX report to %s", latex_report_file)
        with open(latex_report_file, 'w') as f:
            tex = latex.tex_classification_report(report_data,
                                                  self.features, self.classes)
            f.write(tex)

        with rc.get_path("hhulogo.pdf") as logo:
            shutil.copy(logo, path)
        with rc.get_path("hhuarticle.cls") as cls_file:
            shutil.copy(cls_file, path)

        # Attempt to compile latex report
        try:
            logging.info("Compiling report.tex with latexmk: %s",
                         latex_report_file)
            subprocess.check_call([
                "latexmk",
                "-pdf",
                # "-jobname=" + os.path.join(path, "report.pdf"),
                r'-pdflatex=pdflatex -interaction=nonstopmode',
                "report.tex"
            ], cwd=path)
        except subprocess.CalledProcessError as e:
            logging.error("Unable to compile the report file %s: %s",
                          latex_report_file, e)

        for est, data in report_data['estimators'].items():
            self.write_classifier_report(est, data, path)

    def write_classifier_report(self, est_name, est_data, path):
        for cv_est in est_data["CV"]['scores']:
            set_name = lambda file: os.path.join(path, f"{est_name}/{cv_est}/{file}")

            scores_file = set_name('scores.csv')
            os.makedirs(os.path.dirname(scores_file), exist_ok=True)
            with open(scores_file, 'w') as scr:
                scr.write("Metric,Train,Test\n")
                for metric in est_data["CV"]["scores"][cv_est]["train"].keys():
                    scr.write(metric + ",")
                    scr.write(str(est_data["CV"]["scores"][cv_est]["train"][metric]) + ",")
                    scr.write(str(est_data["CV"]["scores"][cv_est]["test"][metric]) + "\n")

            cm_file = set_name('confusion_matrix.json')
            with open(cm_file, 'w') as f:
                confusion_dict = {
                    'C': est_data["CV"]["confusion_matrix"][cv_est]
                }
                json.dump(confusion_dict, f, indent=2)

    def save_estimators(self, trained_estimators, path=None):
        if path is None:
            path = self.cf_args.report_path

        for index, est in enumerate(trained_estimators):
            # Save models
            target_path = os.path.join(path, est.__class__.__name__, str(index))

            os.makedirs(target_path, exist_ok=True)
            model_path = os.path.join(target_path, f"model.joblib")

            joblib.dump(est, model_path)
