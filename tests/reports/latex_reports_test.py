from types import SimpleNamespace

import numpy as np
from sklearn.dummy import DummyClassifier

from rapp.report.latex import tex_dataset_report, tex_performance_overview, tex_fairness_overview
from rapp.report.latex import tex_dataset_plot

from rapp.report.latex.tables import tex_performance_table, tex_fairness
from rapp.report.latex.tables import tex_regression_fairness
from rapp.report.latex.tables import tex_cross_validation

import tests.resources as rc


def test_dataset_report_table__two_groups__two_labels():
    report = {'train': {},
              'test': {}}

    report["train"] = {
        'groups': {'foo': {'foo1': {'outcomes': {'label1': 40, 'label2': 30},
                                    'total': 70},
                           'foo2': {'outcomes': {'label1': 20, 'label2': 60},
                                    'total': 80}},
                   'bar': {'bar1': {'outcomes': {'label1': 30, 'label2': 40},
                                    'total': 70},
                           'bar2': {'outcomes': {'label1': 30, 'label2': 50},
                                    'total': 80}}},
        'outcomes': {
            'label1': 60,
            'label2': 90,
        },
        'total': 150
    }
    report["test"] = {
        'groups': {'foo': {'foo1': {'outcomes': {'label1': 4, 'label2': 3},
                                    'total': 7},
                           'foo2': {'outcomes': {'label1': 2, 'label2': 6},
                                    'total': 8}},
                   'bar': {'bar1': {'outcomes': {'label1': 3, 'label2': 4},
                                    'total': 7},
                           'bar2': {'outcomes': {'label1': 3, 'label2': 5},
                                    'total': 8}}},
        'outcomes': {
            'label1': 6,
            'label2': 9,
        },
        'total': 15
    }

    expected = rc.get_text('reports/data_table_two_groups_two_labels.tex')
    actual = tex_dataset_report(report)

    assert expected == actual


def test_dataset_report_plot__two_groups__two_labels():
    rng = np.random.default_rng(seed=123)

    report = {'train': {},
              'test': {}}

    report["train"] = {
        'groups': {'foo': {'foo1': {'outcomes': rng.integers(3, size=4),
                                    'total': 4},
                           'foo2': {'outcomes': rng.integers(3, size=2),
                                    'total': 2}},
                   'bar': {'bar1': {'outcomes': rng.integers(3, size=3),
                                    'total': 3},
                           'bar2': {'outcomes': rng.integers(3, size=3),
                                    'total': 3}}},
        'outcomes': rng.integers(3, size=12),
        'total': 12
    }
    report["test"] = {
        'groups': {'foo': {'foo1': {'outcomes': rng.integers(3, size=3),
                                    'total': 3},
                           'foo2': {'outcomes': rng.integers(3, size=3),
                                    'total': 3}},
                   'bar': {'bar1': {'outcomes': rng.integers(3, size=3),
                                    'total': 3},
                           'bar2': {'outcomes': rng.integers(3, size=3),
                                    'total': 3}}},
        'outcomes': rng.integers(3, size=12),
        'total': 12
    }

    expected = rc.get_text('reports/data_plot_two_groups_two_labels.tex')
    actual = tex_dataset_plot(report)

    assert expected == actual


def test_dataset_report_plot__no_groups():
    rng = np.random.default_rng(seed=123)

    report = {'train': {},
              'test': {}}

    report["train"] = {
        'groups': {},
        'outcomes': rng.integers(3, size=12),
        'total': 12
    }
    report["test"] = {
        'groups': {},
        'outcomes': rng.integers(3, size=12),
        'total': 12
    }

    expected = rc.get_text('reports/data_plot_no_groups.tex')
    actual = tex_dataset_plot(report)

    assert expected == actual


def test_performance_table__two_metrics():
    estimator = "foobar"
    report = {'train': {},
              'test': {}}
    report["train"] = {
        'scores': {
            'foo': 0,
            'bar': 5}
    }
    report["test"] = {
        'scores': {
            'foo': 5,
            'bar': 0}
    }

    expected = rc.get_text('reports/metrics_table_two_metrics.tex')
    actual = tex_performance_table(estimator, report)

    assert expected == actual


def test_fairness_table__two_groups__two_notions__two_notions__one_measure():
    estimator = "foobar"
    report = {
        'foo': {'notion1': {'train': {'a': {'affected_percent': 10.0}},
                            'test': {'a': {'affected_percent': 4.0}}},
                'notion2': {'train': {'a': {'affected_percent': 8.0}},
                            'test': {'a': {'affected_percent': 7.0}}}},
        'bar': {'notion1': {'train': {'a': {'affected_percent': 6.0}},
                            'test': {'a': {'affected_percent': 2.0}}},
                'notion2': {'train': {'a': {'affected_percent': 8.0}},
                            'test': {'a': {'affected_percent': 10.0}}}}
    }

    expected = rc.get_text('reports/fairness_table_two_groups_two_notions_one_measure.tex')
    actual = tex_fairness(estimator, report)

    assert expected == actual


def test_fairness_regressor_table__two_groups__two_notions():
    estimator = "foobar"
    report = {
        'foo': {'notion1': {'train': 10,
                            'test': 1},
                'notion2': {'train': 0,
                            'test': 2}},
        'bar': {'notion1': {'train': 0,
                            'test': 2},
                'notion2': {'train': 10,
                            'test': 1}}
    }

    expected = rc.get_text('reports/fairness_regressor_table_two_groups_two_notions.tex')
    actual = tex_regression_fairness(estimator, report)

    assert expected == actual


def test_cv_table__three_fold():
    estimator = "foobar"
    report = {'train_foo': [5, 4, 3],
              'train_bar': [5, 4, 3],
              'test_foo': [0, 1, 2],
              'test_bar': [0, 1, 2]}

    expected = rc.get_text('reports/cv_table.tex')
    actual = tex_cross_validation(estimator, report)

    assert expected == actual


def test_performance_overview_table__two_models__two_metrics():
    est1 = DummyClassifier()
    est2 = DummyClassifier()
    pipeline = SimpleNamespace()
    pipeline.estimators = [est1, est2]

    pipeline.performance_results = {est1: {
        'train': {
            'scores': {
                'A': 0.2222,
                'B': 0.5555},
            'confusion_matrix': [[0, 8], [0, 2]]},
        'test': {
            'scores': {
                'A': 0.3333,
                'B': 0.4444},
            'confusion_matrix': [[0, 8], [0, 2]]}}}

    pipeline.performance_results[est2] = pipeline.performance_results[est1]

    expected = rc.get_text('reports/performance_overview_two_models_two_metrics.tex')
    actual = tex_performance_overview(pipeline.performance_results)

    assert expected == actual


def test_fairness_overview_table__two_models__two_notions():
    est1 = DummyClassifier()
    est2 = DummyClassifier()
    pipeline = SimpleNamespace()
    pipeline.estimators = [est1, est2]

    pipeline.fairness_results = {est1: {'Sensitive':
                                            {'C': {'train': {'bar': {'affected_percent': 0.5555,
                                                                     },
                                                             'baz': {'affected_percent': 0.6666,
                                                                     }},
                                                   'test': {'bar': {'affected_percent': 0.6666,
                                                                    },
                                                            'baz': {'affected_percent': 0.9999,
                                                                    }}},
                                             'D': {'train': np.float64(1.1111),
                                                   'test': np.float64(1.2222)}},
                                        'Protected':
                                            {'C': {'train': {'bar': {'affected_percent': 0.1111,
                                                                     },
                                                             'baz': {'affected_percent': 0.3333,
                                                                     }},
                                                   'test': {'bar': {'affected_percent': 0.3333,
                                                                    },
                                                            'baz': {'affected_percent': 0.5555,
                                                                    }}},
                                             'D': {'train': np.float64(2.1111),
                                                   'test': np.float64(2.2222)}}}}

    pipeline.fairness_results[est2] = pipeline.fairness_results[est1]

    expected = rc.get_text('reports/fairness_overview_two_models_two_notions.tex')
    actual = tex_fairness_overview(pipeline.fairness_results)

    assert expected == actual
