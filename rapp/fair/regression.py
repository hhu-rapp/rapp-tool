import numpy as np


def regression_individual_fairness(X, y, z, pred, fav_label=1):
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
    z_values, z_group_counts = np.unique(z, return_counts=True)
    majority_group = z_values[np.argmax(z_group_counts)]

    y_s1 = y[z != majority_group]
    y_s2 = y[z == majority_group]
    y_pred_s1 = pred[z != majority_group]
    y_pred_s2 = pred[z == majority_group]
    n1 = len(y_s1)
    n2 = len(y_s2)

    fairness_penalty = 0
    for yi, yi_pred in zip(y_s1, y_pred_s1):
        for yj, yj_pred in zip(y_s2, y_pred_s2):
            fairness_penalty += cross_group_fairness_weights(yi, yj) * (yi_pred - yj_pred) ** 2
    fairness_penalty = 1 / (n1 + n2) * fairness_penalty  # normalization

    return fairness_penalty


def regression_group_fairness(X, y, z, pred, fav_label=1):
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
    z_values, z_group_counts = np.unique(z, return_counts=True)
    majority_group = z_values[np.argmax(z_group_counts)]

    y_s1 = y[z != majority_group]
    y_s2 = y[z == majority_group]
    y_pred_s1 = pred[z != majority_group]
    y_pred_s2 = pred[z == majority_group]
    n1 = len(y_s1)
    n2 = len(y_s2)

    fairness_penalty = 0
    for yi, yi_pred in zip(y_s1, y_pred_s1):
        for yj, yj_pred in zip(y_s2, y_pred_s2):
            fairness_penalty += cross_group_fairness_weights(yi, yj) * (yi_pred - yj_pred)
    fairness_penalty = (1 / (n1 + n2) * fairness_penalty) ** 2  # normalization

    return fairness_penalty


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
    return np.exp(-(yi - yj) ** 2)
