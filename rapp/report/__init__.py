import numpy as np

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

from rapp.fair.notions import clf_fairness
from rapp.fair.notions import group_fairness
from rapp.fair.notions import equality_of_opportunity
from rapp.fair.notions import predictive_equality

import os
import json

from datetime import datetime
from rapp.report import latex


class ClassifierReport(object):

    def __init__(self, estimators, config_args) -> None:
        """
        Parameters
        ----------
        estimators: list of already trained classifiers.

        config_args: Parser arguments from parser.RappConfigParser.
        """
        super().__init__()

        self.estimators = estimators
        self.cf_args = config_args

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

    def calculate_reports(self, X_train, y_train, z_train, X_test, y_test, z_test):
        reports = {}
        sets = [('train', X_train, y_train, z_train),
                ('test', X_test, y_test, z_test)]

        for (set_name, X, y, z) in sets:
            set_rep = self.calculate_set_statistics(X, y, z)
            reports[set_name] = set_rep

        estimator_reports = {}
        for est in self.estimators:
            est_rep = {}
            for (set_name, X, y, z) in sets:
                est_rep[set_name] = self.calculate_single_set_report(est, X, y, z)
            estimator_reports[self.clf_name(est)] = est_rep
        reports['estimators'] = estimator_reports

        return reports

    def clf_name(self, estimator):
        return estimator.__class__.__name__

    def calculate_set_statistics(self, X, y, z):
        set_stats = {'total': len(y),
                     'outcomes': {}}

        values = y.unique()
        for v in values:
            num = len(y[y == v])
            set_stats['outcomes'][v] = num

        return set_stats

    def calculate_single_set_report(self, estimator, X, y, z):
        pred = estimator.predict(X)

        scorings = {}
        scorings['scores'] = self.get_score_dict(y, pred)
        C = confusion_matrix(np.round(y).astype(int), np.round(pred).astype(int))#.ravel()
        # tn, fp, fn, tp = confusion_matrix(np.round(y).astype(int), np.round(pred).astype(int)).ravel()
        '''
        scorings['confusion_matrix'] = {
            'tp': int(tp),
            'fp': int(fp),
            'tn': int(tn),
            'fn': int(fn),
        }
        '''
        scorings['confusion_matrix'] = {'C': C.tolist()}
        fairness = {}
        for group in z.columns:
            fairness[group] = {}
            for notion, fun in self.used_fairnesses.items():
                fairness[group][notion] = \
                    clf_fairness(estimator, fun, X, y, z[group], pred)
        scorings["fairness"] = fairness

        return scorings

    def get_score_dict(self, y, pred):
        score_dict = {}
        for scoring_name, fun in self.used_scores.items():
            score_dict[scoring_name] = fun(np.round(y).astype(int), np.round(pred).astype(int))
        return score_dict

    def write_report(self, report_data, path=None):
        if path is None:
            sql_base_name = os.path.splitext(
                os.path.basename(self.cf_args.sql_filename))[0]
            # path = f"reports/{sql_base_name}-{datetime.now().isoformat()}/"
            path = f"reports/{sql_base_name}-testing/"

        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            print(f"Could not write report to {path}:", e)

        with open(path+"/report.json", 'w') as r:
            json.dump(report_data, r, indent=2)

        with open(path+"/report.tex", 'w') as f:
            tex = latex.tex_classification_report(report_data)
            f.write(tex)

        for est, data in report_data['estimators'].items():
            self.write_classifier_report(est, data, path)

    def write_classifier_report(self, est_name, est_data, path):
        data_pre = path + '/' + est_name + "_"

        scores_file = data_pre + 'scores.csv'
        with open(scores_file, 'w') as scr:
            scr.write("Metric,Train,Test\n")
            for metric in est_data["train"]["scores"].keys():
                scr.write(metric + ",")
                scr.write(str(est_data["train"]["scores"][metric]) + ",")
                scr.write(str(est_data["test"]["scores"][metric]) + "\n")

        cm_file = data_pre + 'confusion_matrix.json'
        with open(cm_file, 'w') as f:
            confusion_dict = {
                'train': est_data["train"]["confusion_matrix"],
                'test': est_data["test"]["confusion_matrix"]
            }
            json.dump(confusion_dict, f, indent=2)
