from types import SimpleNamespace

import numpy as np
import pytest
from sklearn.dummy import DummyClassifier
from rapp.util import estimator_name
from rapp.gui.widgets.evaluation_views import InitialView, ModelViewCLF

from tests.gui.fixture import gui, GuiTestApi


@pytest.fixture
def clf_pipeline():
    est1 = DummyClassifier()
    est2 = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.estimators = [est1, est2]

    rng = np.random.default_rng(seed=123)
    X_train = pd.DataFrame(rng.random((6, 2)), columns=['foo', 'bar'])
    y_train = pd.DataFrame(rng.integers(3, size=(6,)), columns=['baz'])

    est1.fit(X_train, y_train.to_numpy().ravel())
    est2.fit(X_train, y_train.to_numpy().ravel())

    pipeline.data = {'train': {'X': X_train, 'y': y_train}}

    pipeline.type = 'classification'
    pipeline.score_functions = {'A': None,
                                'B': None}

    pipeline.performance_results = {est1: {
        'train': {
            'scores': {
                'A': 0.2,
                'B': 0.5},
            'confusion_matrix': [[0, 8], [0, 2]]}}}
    pipeline.performance_results[est2] = pipeline.performance_results[est1]

    return pipeline

@pytest.fixture
def interpretability_clf(gui: GuiTestApi, clf_pipeline):
    gui.tabs.setTabEnabled(gui.widget.interpretability_tab_index, True)
    gui.populate_interpretability_tab(clf_pipeline)
    return gui


def test_widget_type_initial_view(interpretability_clf: GuiTestApi):
    actual = type(interpretability_clf.current_view())
    expected = InitialView
    assert actual == expected, \
        f"The current view widget type should be {expected}, but is {actual}"


def test_summary_table_in_initial_view(interpretability_clf: GuiTestApi):
    labels = interpretability_clf.current_view().summary_table.labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Model': ['DummyClassifier', 'DummyClassifier'],
                'A': ['0.200', '0.200'],
                'B': ['0.500', '0.500']}
    assert actual == expected, \
        f"The values in the summary table should be {expected}, but are {actual}"
