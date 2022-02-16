from types import SimpleNamespace

import numpy as np
import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from rapp import sqlbuilder
from rapp.npipeline import _parse_estimators
from rapp.npipeline import _load_sql_query
from rapp.npipeline import _load_test_split_from_dataframe

import tests.resources as rc


def test_estimator_parsing():
    ids = ["DT", "NN", "SVM"]
    mode = 'classification'

    estimators = _parse_estimators(ids, mode)

    errors = []
    if not isinstance(estimators[0], DecisionTreeClassifier):
        errors.append("First element is not a decision tree classifier but "
                      f"{type(estimators[0])}")
    if not isinstance(estimators[1], MLPClassifier):
        errors.append("Second element is not an MLPClassifier but "
                      f"{type(estimators[1])}")
    if not isinstance(estimators[2], SVC):
        errors.append("Third element is not an SVM classifier but "
                      f"{type(estimators[2])}")

    assert not errors, "\n".join(errors)


def test_regression_estimator_parsing():
    ids = ["DT"]
    mode = 'regression'

    estimators = _parse_estimators(ids, mode)
    dt = estimators[0]

    assert isinstance(dt, DecisionTreeRegressor), "DT Regressor not loaded"


def test_sql_file_loading():
    test_sql = "sql/short.sql"

    # Mock config.
    cf = SimpleNamespace()
    cf.sql_file = rc.get_path(test_sql)

    sql = _load_sql_query(cf)
    expected = rc.get_text(test_sql)

    assert sql == expected


def test_sql_template_loading():
    # Mock config.
    cf = SimpleNamespace()
    cf.studies_id = "cs"
    cf.features_id = "first_term_ects"
    cf.labels_id = "3_dropout"

    sql = _load_sql_query(cf)
    expected = sqlbuilder.load_sql("cs_first_term_ects", "3_dropout")

    assert sql == expected


def test_df_train_split():
    # Helper functions to create data.
    def raw_data(n): return {'a': n, 'b': f'c{n % 2}', 'y': n, 'z': n}
    def x_data(n): return {'a': n, 'z': n, 'b_c0': 1 - n % 2, 'b_c1': n % 2}

    # Setup data frame
    df = pd.DataFrame([
        raw_data(0), raw_data(1), raw_data(2), raw_data(3), raw_data(4),
        raw_data(5), raw_data(6), raw_data(7), raw_data(8), raw_data(9),
    ])

    # Setup config
    cf = SimpleNamespace()
    cf.label_name = 'y'
    cf.categorical = ['b']
    cf.sensitive_attributes = ['z']

    data = _load_test_split_from_dataframe(df, cf, random_state=42)

    train_ids = [5, 0, 7, 2, 9, 4, 3, 6]  # Selected with random_state = 42.
    train_features = [x_data(n) for n in train_ids]
    test_ids = [8, 1]  # Selected with random_state = 42.
    test_features = [x_data(n) for n in test_ids]

    expected = {
        "train": {
            "X": pd.DataFrame(train_features, index=train_ids),
            "y": pd.DataFrame(train_ids, index=train_ids),
            "z": pd.DataFrame(train_ids, index=train_ids),
        },
        "test": {
            "X": pd.DataFrame(test_features, index=test_ids),
            "y": pd.DataFrame(test_ids, index=test_ids),
            "z": pd.DataFrame(test_ids, index=test_ids),
        },
    }

    errors = []
    for mode in ["train", "test"]:
        for part in ["X", "y", "z"]:
            lhs = data[mode][part].values.tolist()
            rhs = expected[mode][part].values.tolist()
            if not (lhs == rhs):
                errors.append(f"{part}_{mode} values do not match:"
                              f"{lhs}, {rhs}")
    assert not errors, "\n".join(errors)


def test_df_train_split_without_label_name():
    # Helper functions to create data.
    def raw_data(n): return {'a': n, 'b': f'c{n % 2}', 'z': n, 'y': n+1}
    def x_data(n): return {'a': n, 'z': n, 'b_c0': 1 - n % 2, 'b_c1': n % 2}

    # Setup data frame
    df = pd.DataFrame([
        raw_data(0), raw_data(1), raw_data(2), raw_data(3), raw_data(4),
        raw_data(5), raw_data(6), raw_data(7), raw_data(8), raw_data(9),
    ])

    # Setup config
    cf = SimpleNamespace()
    cf.categorical = ['b']
    cf.sensitive_attributes = ['z']

    data = _load_test_split_from_dataframe(df, cf, random_state=42)

    train_ids = [5, 0, 7, 2, 9, 4, 3, 6]  # Selected with random_state = 42.
    train_features = [x_data(n) for n in train_ids]
    test_ids = [8, 1]  # Selected with random_state = 42.
    test_features = [x_data(n) for n in test_ids]

    expected = {
        "train": {
            "X": pd.DataFrame(train_features, index=train_ids),
            "y": pd.DataFrame([i+1 for i in train_ids], index=train_ids),
            "z": pd.DataFrame(train_ids, index=train_ids),
        },
        "test": {
            "X": pd.DataFrame(test_features, index=test_ids),
            "y": pd.DataFrame([i+1 for i in test_ids], index=test_ids),
            "z": pd.DataFrame(test_ids, index=test_ids),
        },
    }

    errors = []
    for mode in ["train", "test"]:
        for part in ["X", "y", "z"]:
            lhs = data[mode][part].values.tolist()
            rhs = expected[mode][part].values.tolist()
            if not (lhs == rhs):
                errors.append(f"{part}_{mode} values do not match:"
                              f"{lhs}, {rhs}")
    assert not errors, "\n".join(errors)


def test_df_train_split_with_label_name_None():
    # Helper functions to create data.
    def raw_data(n): return {'a': n, 'b': f'c{n % 2}', 'z': n, 'y': n+1}
    def x_data(n): return {'a': n, 'z': n, 'b_c0': 1 - n % 2, 'b_c1': n % 2}

    # Setup data frame
    df = pd.DataFrame([
        raw_data(0), raw_data(1), raw_data(2), raw_data(3), raw_data(4),
        raw_data(5), raw_data(6), raw_data(7), raw_data(8), raw_data(9),
    ])

    # Setup config
    cf = SimpleNamespace()
    cf.categorical = ['b']
    cf.sensitive_attributes = ['z']
    cf.label_name = None

    data = _load_test_split_from_dataframe(df, cf, random_state=42)

    train_ids = [5, 0, 7, 2, 9, 4, 3, 6]  # Selected with random_state = 42.
    train_features = [x_data(n) for n in train_ids]
    test_ids = [8, 1]  # Selected with random_state = 42.
    test_features = [x_data(n) for n in test_ids]

    expected = {
        "train": {
            "X": pd.DataFrame(train_features, index=train_ids),
            "y": pd.DataFrame([i+1 for i in train_ids], index=train_ids),
            "z": pd.DataFrame(train_ids, index=train_ids),
        },
        "test": {
            "X": pd.DataFrame(test_features, index=test_ids),
            "y": pd.DataFrame([i+1 for i in test_ids], index=test_ids),
            "z": pd.DataFrame(test_ids, index=test_ids),
        },
    }

    errors = []
    for mode in ["train", "test"]:
        for part in ["X", "y", "z"]:
            lhs = data[mode][part].values.tolist()
            rhs = expected[mode][part].values.tolist()
            if not (lhs == rhs):
                errors.append(f"{part}_{mode} values do not match:"
                              f"{lhs}, {rhs}")
    assert not errors, "\n".join(errors)


def test_df_train_split__no_categorical():
    # Helper functions to create data.
    def raw_data(n): return {'a': n, 'b': n, 'y': n, 'z': n}
    def x_data(n): return {'a': n, 'b': n, 'z': n}

    # Setup data frame
    df = pd.DataFrame([
        raw_data(0), raw_data(1), raw_data(2), raw_data(3), raw_data(4),
        raw_data(5), raw_data(6), raw_data(7), raw_data(8), raw_data(9),
    ])

    # Setup config
    cf = SimpleNamespace()
    cf.label_name = 'y'
    cf.categorical = []
    cf.sensitive_attributes = ['z']

    data = _load_test_split_from_dataframe(df, cf, random_state=42)

    train_ids = [5, 0, 7, 2, 9, 4, 3, 6]  # Selected with random_state = 42.
    train_features = [x_data(n) for n in train_ids]
    test_ids = [8, 1]  # Selected with random_state = 42.
    test_features = [x_data(n) for n in test_ids]

    expected = {
        "train": {
            "X": pd.DataFrame(train_features, index=train_ids),
            "y": pd.DataFrame(train_ids, index=train_ids),
            "z": pd.DataFrame(train_ids, index=train_ids),
        },
        "test": {
            "X": pd.DataFrame(test_features, index=test_ids),
            "y": pd.DataFrame(test_ids, index=test_ids),
            "z": pd.DataFrame(test_ids, index=test_ids),
        },
    }

    errors = []
    for mode in ["train", "test"]:
        for part in ["X", "y", "z"]:
            lhs = data[mode][part].values.tolist()
            rhs = expected[mode][part].values.tolist()
            if not (lhs == rhs):
                errors.append(f"{part}_{mode} values do not match:"
                              f"{lhs}, {rhs}")
    assert not errors, "\n".join(errors)
