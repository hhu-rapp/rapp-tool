from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.utils.validation import check_is_fitted

from rapp import sqlbuilder
from rapp.fair.notions import group_fairness, predictive_equality
from rapp.npipeline import Pipeline, _parse_estimators
from rapp.npipeline import _load_sql_query
from rapp.npipeline import _load_test_split_from_dataframe
from rapp.npipeline import train_models
from rapp.npipeline import evaluate_estimator_fairness
from rapp.npipeline import evaluate_estimators_performance
from rapp.parser import RappConfigParser

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
    def raw_data(n): return {'a': n, 'b': f'c{n % 2}', 'z': n, 'y': n + 1}
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
            "y": pd.DataFrame([i + 1 for i in train_ids], index=train_ids),
            "z": pd.DataFrame(train_ids, index=train_ids),
        },
        "test": {
            "X": pd.DataFrame(test_features, index=test_ids),
            "y": pd.DataFrame([i + 1 for i in test_ids], index=test_ids),
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
    def raw_data(n): return {'a': n, 'b': f'c{n % 2}', 'z': n, 'y': n + 1}
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
            "y": pd.DataFrame([i + 1 for i in train_ids], index=train_ids),
            "z": pd.DataFrame(train_ids, index=train_ids),
        },
        "test": {
            "X": pd.DataFrame(test_features, index=test_ids),
            "y": pd.DataFrame([i + 1 for i in test_ids], index=test_ids),
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


def test_load_data_from_query():
    query = "select * from Student order by Pseudonym Limit 100"
    args = ['-t', 'classification', '-f', rc.get_path('test.db'),
            '-sq', query]
    pipeline = Pipeline(RappConfigParser().parse_args(args))

    X_train, y_train, z_train = pipeline.get_data('train')
    X_test, y_test, z_test = pipeline.get_data('test')

    assert (len(X_train) == len(y_train) == len(z_train) == 80
            and
            len(X_test) == len(y_test) == len(z_test) == 20)


def test_load_data_from_sql_templating():
    args = ['-t', 'classification', '-f', rc.get_path('test.db'),
            '-sid', 'cs', '-fid', 'first_term_ects', '-lid', '3_dropout']
    pipeline = Pipeline(RappConfigParser().parse_args(args))

    X_train, y_train, z_train = pipeline.get_data('train')
    X_test, y_test, z_test = pipeline.get_data('test')

    assert (len(X_train) == len(y_train) == len(z_train) == 194)
    assert (len(X_test) == len(y_test) == len(z_test) == 49)


def test_load_data_from_sql_file():
    sql_file = rc.get_path('sql/short.sql')
    args = ['-t', 'classification', '-f', rc.get_path('test.db'),
            '-sf', sql_file]
    pipeline = Pipeline(RappConfigParser().parse_args(args))

    X_train, y_train, z_train = pipeline.get_data('train')
    X_test, y_test, z_test = pipeline.get_data('test')

    assert (len(X_train) == len(y_train) == len(z_train)
            == 80), "Wrong amount of training data"
    assert (len(X_test) == len(y_test) == len(
        z_test) == 20), "Wrong amount of test data"


def test_load_correct_sql_query_from_file():
    sql_file = rc.get_path('sql/short.sql')
    args = ['-t', 'classification', '-f', rc.get_path('test.db'),
            '-sf', sql_file]
    pipeline = Pipeline(RappConfigParser().parse_args(args))

    expected = "SELECT * FROM student ORDER BY Pseudonym LIMIT 100\n"
    actual = pipeline.sql_query

    assert expected == actual, "SQL query does not match"


def test_training_with_cross_validation():
    est = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.estimators = [est]
    pipeline.score_functions = {'Accuracy': accuracy_score}
    pipeline.cross_validation = {}  # Assumed to be present but empty.

    rng = np.random.default_rng(seed=123)
    X_train = rng.random((100, 2))
    y_train = rng.integers(2, size=(100, 1))
    pipeline.get_data = lambda _: (X_train, y_train, None)

    train_models(pipeline, cross_validation=True)

    expected = set(['train_Accuracy', 'test_Accuracy', 'estimator',
                    'score_time', 'fit_time'])
    actual = set(pipeline.cross_validation[est].keys())

    assert expected == actual


def test_training_without_cross_validation():
    est = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.estimators = [est]
    pipeline.score_functions = {'Accuracy': accuracy_score}
    pipeline.cross_validation = {}  # Assumed to be present but empty.

    rng = np.random.default_rng(seed=123)
    X_train = rng.random((100, 2))
    y_train = rng.integers(2, size=(100, 1))
    pipeline.get_data = lambda _: (X_train, y_train, None)

    train_models(pipeline, cross_validation=False)

    assert pipeline.cross_validation == {}


def test_training_fits_each_estimator():
    est1 = DummyClassifier()
    est2 = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.estimators = [est1, est2]
    pipeline.score_functions = {'Accuracy': accuracy_score}
    pipeline.cross_validation = {}  # Assumed to be present but empty.

    rng = np.random.default_rng(seed=123)
    X_train = rng.random((100, 2))
    y_train = rng.integers(2, size=(100, 1))
    pipeline.get_data = lambda _: (X_train, y_train, None)

    train_models(pipeline, cross_validation=False)

    try:
        check_is_fitted(est1)
        check_is_fitted(est2)
    except Exception:
        pytest.fail("Not all estimators where fitted turing model training.")


def test_fairness_results_structure():
    rng = np.random.default_rng(seed=123)
    X_train = rng.random((10, 2))
    y_train = rng.integers(2, size=(10,))
    z_train = pd.DataFrame(rng.integers(2, size=(10, 1)),
                           columns=['protected'])
    data = {'train': {'X': X_train, 'y': y_train, 'z': z_train}}

    est = DummyClassifier(strategy='constant', constant=1)
    est.fit(X_train, y_train)

    notions = {'pred parity': predictive_equality,
               'statistical': group_fairness}

    results = evaluate_estimator_fairness(est, data, notions)

    expected = {
        'protected': {
            'pred parity': {
                'train': {
                    0: {
                        "affected_total": 6,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 6, 0, 1]},
                    1: {
                        "affected_total": 2,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 2, 0, 1]},
                }},
            'statistical': {
                'train': {
                    0: {
                        "affected_total": 7,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 6, 0, 1]},
                    1: {
                        "affected_total": 3,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 2, 0, 1]},
                }}}}
    assert expected == results


def test_fairness_results_only_checks_given_attributes():
    rng = np.random.default_rng(seed=123)
    X_train = rng.random((10, 2))
    y_train = rng.integers(2, size=(10,))
    z_train = pd.DataFrame(rng.integers(2, size=(10, 2)),
                           columns=['protected', 'sensitive'])
    data = {'train': {'X': X_train, 'y': y_train, 'z': z_train}}

    est = DummyClassifier(strategy='constant', constant=1)
    est.fit(X_train, y_train)

    notions = {'pred parity': predictive_equality,
               'statistical': group_fairness}

    results = evaluate_estimator_fairness(est, data, notions,
                                          protected_attributes='protected')

    expected = {
        'protected': {
            'pred parity': {
                'train': {
                    0: {
                        "affected_total": 6,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 6, 0, 2]},
                    1: {
                        "affected_total": 2,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 2, 0, 0]},
                }},
            'statistical': {
                'train': {
                    0: {
                        "affected_total": 8,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 6, 0, 2]},
                    1: {
                        "affected_total": 2,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 2, 0, 0]},
                }}}}
    assert expected == results


def test_fairness_results_for_all_protected_attributes():
    rng = np.random.default_rng(seed=123)
    X_train = rng.random((10, 2))
    y_train = rng.integers(2, size=(10,))
    z_train = pd.DataFrame(rng.integers(2, size=(10, 2)),
                           columns=['protected', 'sensitive'])
    data = {'train': {'X': X_train, 'y': y_train, 'z': z_train}}

    est = DummyClassifier(strategy='constant', constant=1)
    est.fit(X_train, y_train)

    notions = {'pred parity': predictive_equality}

    results = evaluate_estimator_fairness(est, data, notions)

    expected = {
        'protected': {
            'pred parity': {
                'train': {
                    0: {
                        "affected_total": 6,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 6, 0, 2]},
                    1: {
                        "affected_total": 2,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 2, 0, 0]},
                }}},
        'sensitive': {
            'pred parity': {
                'train': {
                    0: {
                        "affected_total": 1,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 1, 0, 2]},
                    1: {
                        "affected_total": 7,
                        "affected_percent": 1.,
                        "confusion_matrix": [0, 7, 0, 0]},
                }}}}
    assert expected == results


def test_performance_results_structure():
    rng = np.random.default_rng(seed=123)
    X_train = rng.random((10, 2))
    y_train = rng.integers(2, size=(10,))
    z_train = pd.DataFrame(rng.integers(2, size=(10, 2)),
                           columns=['protected', 'sensitive'])
    data = {'train': {'X': X_train, 'y': y_train, 'z': z_train}}

    est = DummyClassifier(strategy='constant', constant=1)
    est.fit(X_train, y_train)

    scores = {'Accuracy': accuracy_score,
              'Balanced Accuracy': balanced_accuracy_score}

    results = evaluate_estimators_performance(est, data, scores)

    expected = {'train' :{
                'scores':{
                    'Accuracy' : 0.2,
                    'Balanced Accuracy' : 0.5},
                'confusion_matrix' : [[0, 8], [0, 2]]}}

    assert expected == results
