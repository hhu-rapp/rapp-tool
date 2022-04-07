import numpy as np
from sklearn.metrics import confusion_matrix


def regression_individual_fairness(X, y, z, pred, fav_label=None):
    """
    Berk 2017 - A Convex Framework for Fair Regression

    Parameters
    ----------
    X: pandas DataFrame
    y: pandas DataFrame
    z: pandas DataFrame
    pred: pandas DataFrame
    fav_label: numeric

    Returns
    -------

    """
    fair = {}

    y_s1 = y[z == 0]
    y_s2 = y[z == 1]
    y_pred_s1 = pred[z == 0]
    y_pred_s2 = pred[z == 1]
    n1 = len(y_s1)
    n2 = len(y_s2)

    fairness_penalty = 0
    for yi, yi_pred in zip(y_s1, y_pred_s1):
        for yj, yj_pred in zip(y_s2, y_pred_s2):
            fairness_penalty += cross_group_fairness_weights( yi, yj) * (yi_pred - yj_pred) ** 2
    fairness_penalty = 1 / (n1 + n2) * fairness_penalty  # normalization

    fair = {
        "Individual Fairness": fairness_penalty
    }

    return fair


def regression_group_fairness(X, y, z, pred, fav_label=None):
    """
    Berk 2017 - A Convex Framework for Fair Regression

    Parameters
    ----------
    X: pandas DataFrame
    y: pandas DataFrame
    z: pandas DataFrame
    pred: pandas DataFrame
    fav_label: numeric

    Returns
    -------

    """
    fair = {}

    y_s1 = y[z == 0]
    y_s2 = y[z == 1]
    y_pred_s1 = pred[z == 0]
    y_pred_s2 = pred[z == 1]
    n1 = len(y_s1)
    n2 = len(y_s2)

    fairness_penalty = 0
    for yi, yi_pred in zip(y_s1, y_pred_s1):
        for yj, yj_pred in zip(y_s2, y_pred_s2):
            fairness_penalty += cross_group_fairness_weights( yi, yj) * (yi_pred - yj_pred)
    fairness_penalty = (1 / (n1 + n2) * fairness_penalty) ** 2  # normalization

    fair = {
        "Group Fairness": fairness_penalty
    }

    return fair


def cross_group_fairness_weights(yi, yj):
    """
    Berk 2017 - A Convex Framework for Fair Regression

    Parameters
    ----------
    yi: numeric
    yj: numeric

    Returns
    -------

    """
    return np.exp(-(yi - yj)**2)


def clf_fairness(clf, fairness, X, y, Z, pred=None, fav_label=1):
    """
    Assesses the fairness of the given classifier over the data (X, y, z).
    For each column c in `z`, a dictionary of the following form is returned

        {c: {
                0: {"favourable_outcome": number_with_fav_outcome,
                    "unfavourable_outcome": number_without_fav_outcome,
                    "confusion_matrix": ... },
                1: {"favourable_outcome": number_with_fav_outcome,
                    "unfavourable_outcome": number_without_fav_outcome,
                    "confusion_matrix": ... },
                # ...
            },
         # ...
         }

    where one key for each unique value of the respective column exists.

    Parameters
    ----------
    clf: Classifier with a `.predict(X)` method.
    fairness: Fairness function from `rapp.fair.notions`.
    X: Feature values of the input data, assumed as Pandas data frame.
    y: Ground-truth labels of the input data.
    Z: Sensitive attributes for input data.
    pred: (default=None)
        Predictions from classifier for X. If `pred=None`, `clf.predict(X)` will be called.
    fav_label: (default=1)
        Value of the favourable outcome of the prediction.

    Returns
    -------
    dict: See description.
    """
    if pred is None:
        pred = clf.predict(X)

    fair_results = fairness(X, y, Z, pred, fav_label)

    return {'outcomes': fair_results}


def __get_confusion_matrix(y_true, y_pred):
    return confusion_matrix(y_true, y_pred).ravel().tolist()


def group_fairness(X, y, z, pred, fav_label=1):
    fair = {}

    values = z.unique()
    for v in values:
        mask = (z == v)
        pred_v = pred[mask]

        fav = pred_v[pred_v == fav_label]

        affected_percent = 0 if len(pred_v) == 0 else len(fav) / len(pred_v)

        fair[v] = {
            "affected_total": len(fav),
            "affected_percent": affected_percent,
            "confusion_matrix": __get_confusion_matrix(y[mask], pred[mask])
        }

    return fair


def predictive_equality(X, y, z, pred, fav_label=1):
    fair = {}

    values = z.unique()
    for v in values:
        mask = (z == v)
        mask_v = np.logical_and(mask, y != fav_label)
        pred_v = pred[mask_v]

        fav = pred_v[pred_v == fav_label]

        affected_percent = 0 if len(pred_v) == 0 else len(fav) / len(pred_v)

        fair[v] = {
            "affected_total": len(fav),
            "affected_percent": affected_percent,
            "confusion_matrix": __get_confusion_matrix(y[mask], pred[mask])
        }

    return fair


def equality_of_opportunity(X, y, z, pred, fav_label=1):
    fair = {}

    values = z.unique()
    for v in values:
        mask = (z == v)
        pred_v = pred[mask & (y == fav_label)]

        fav = pred_v[pred_v == fav_label]

        affected_percent = 0 if len(pred_v) == 0 else len(fav) / len(pred_v)

        fair[v] = {
            "affected_total": len(fav),
            "affected_percent": affected_percent,
            "confusion_matrix": __get_confusion_matrix(y[mask], pred[mask])
        }

    return fair
