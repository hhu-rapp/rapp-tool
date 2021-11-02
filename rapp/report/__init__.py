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

        self.sensitive = config_args.sensitive_attribute

        self.used_scores = {
            'Accuracy': accuracy_score,
            'Balanced Accuracy': balanced_accuracy_score,
            'F1': lambda x, y: f1_score(x, y, average='macro'),
            'Recall': lambda x, y: recall_score(x, y, average='macro'),
            'Precision': lambda x, y: precision_score(x, y, average='macro'),
            'Area under ROC': roc_auc_score,
        }


    def calculate_reports(self, X_train, y_train, X_test, y_test):
        reports = {}

        for est in self.estimators:
            est_rep = {}
            for (set_name, X, y) in [('train', X_train, y_train),
                                     ('test', X_test, y_test)]:
                est_rep[set_name] = self.calculate_single_set_report(est, X, y)
            reports[self.clf_name(est)] = est_rep

        return reports


    def clf_name(self, estimator):
        return estimator.__class__.__name__


    def calculate_single_set_report(self, estimator, X, y):
        pred = estimator.predict(X)

        scorings = {}
        scorings['scores'] = self.get_score_dict(y, pred)
        tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
        scorings['confusion_matrix'] = {
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn,
        }

        return scorings

    def get_score_dict(self, y, pred):
        score_dict = {}
        for scoring_name, fun in self.used_scores.items():
            score_dict[scoring_name] = fun(y, pred)
        return score_dict
