
import numpy as np
import pandas as pd
from rapp.fair import notions


def test_key_error_problem_for_regression_group_fairness():
    """
    Regression test as running the regression_group_fairness function
    yielded a key error due to trying to go over the indices 0..n instead
    of the indices present in the respective dataframes.
    """
    X = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5]})
    y = pd.DataFrame([0.1, 0.2, 0.3, 0.4, 0.5])
    z = pd.DataFrame([0, 0, 1, 1, 0])
    pred = pd.DataFrame([0.2, 0.2, 0.2, 0.2, 0.2])

    try:
        fair = notions.regression_group_fairness(X, y, z, pred)
    except KeyError as err:
        assert False, f"KeyError raised, {err}"


def test_key_error_problem_for_regression_individual_fairness():
    """
    Regression test as running the regression_individual_fairness function
    yielded a key error due to trying to go over the indices 0..n instead
    of the indices present in the respective dataframes.
    """
    X = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5]})
    y = pd.DataFrame([0.1, 0.2, 0.3, 0.4, 0.5])
    z = pd.DataFrame([0, 0, 1, 1, 0])
    pred = pd.DataFrame([0.2, 0.2, 0.2, 0.2, 0.2])

    try:
        fair = notions.regression_individual_fairness(X, y, z, pred)
    except KeyError as err:
        assert False, f"KeyError raised, {err}"


def test_use_of_fav_label_group_regression_fairness():
    """
    Regression test as running the regression_group_fairness function
    lead to a division by zero error if the domain of z is neither containing
    0 nor 1, which is the case with categorical z variables.
    """
    X = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5]})
    y = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    z = np.array(['fav', 'fav', 'nofav', 'nofav', 'fav'])
    pred = np.array([0.2, 0.2, 0.2, 0.2, 0.2])

    try:
        fair = notions.regression_group_fairness(X, y, z, pred)
    except ZeroDivisionError as err:
        assert False, f"ZeroDivisionError raised, {err}"


def test_use_of_fav_label_individual_regression_fairness():
    """
    Regression test as running the regression_individual_fairness function
    lead to a division by zero error if the domain of z is neither containing
    0 nor 1, which is the case with categorical z variables.
    """
    X = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": [1, 2, 3, 4, 5]})
    y = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    z = np.array(['fav', 'fav', 'nofav', 'nofav', 'fav'])
    pred = np.array([0.2, 0.2, 0.2, 0.2, 0.2])

    try:
        fair = notions.regression_individual_fairness(X, y, z, pred)
    except ZeroDivisionError as err:
        assert False, f"ZeroDivisionError raised, {err}"
