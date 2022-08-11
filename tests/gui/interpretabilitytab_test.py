from types import SimpleNamespace

import numpy as np
import pandas as pd
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


def test_no_widgets_in_header_in_initial_view(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)

    actual = interpretability_clf.header_layout.count()
    expected = 0
    assert actual == expected, \
        f"The number of widgets in the header layout should be {expected}, but is {actual}"


def test_click_on_model_in_initial_view(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)
    labels = interpretability_clf.current_view().summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_clf.click(labels[key][model_idx])

    actual = type(interpretability_clf.current_view())
    expected = ModelViewCLF
    assert actual == expected, \
        f"The current view widget type should be {expected}, but is {actual}"


def test_two_widgets_in_header_in_model_view(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)
    labels = interpretability_clf.current_view().summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_clf.click(labels[key][model_idx])

    actual = interpretability_clf.header_layout.count()
    expected = 2
    assert actual == expected, \
        f"The number of widgets in the header layout should be {expected}, but is {actual}"


def test_model_label_in_header_in_model_view(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)
    labels = interpretability_clf.current_view().summary_table.labels

    est2 = DummyClassifier()

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_clf.click(labels[key][model_idx])

    actual = interpretability_clf.header_layout.itemAt(1).widget().text()
    expected = f'Model : {estimator_name(est2)}'
    assert actual == expected, \
        f"The current view widget type should be {expected}, but is {actual}"


def test_click_back_button_in_model_view(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)
    labels = interpretability_clf.current_view().summary_table.labels

    est2 = DummyClassifier()

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_clf.click(labels[key][model_idx])

    back_button = interpretability_clf.header_layout.itemAt(0).widget()
    interpretability_clf.click(back_button)

    actual = type(interpretability_clf.current_view())
    expected = InitialView
    assert actual == expected, \
        f"The current view widget type should be {expected}, but is {actual}"


def test_number_of_tabs_in_model_view_clf(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)
    labels = interpretability_clf.current_view().summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_clf.click(labels[key][model_idx])

    actual = interpretability_clf.current_view().tabs.count()
    expected = 3
    assert actual == expected, \
        f"The number of tabs in the model view should be {expected}, but is {actual}"


def test_dataframe_in_model_view_clf(interpretability_clf: GuiTestApi):
    interpretability_clf.tabs.setCurrentIndex(interpretability_clf.widget.interpretability_tab_index)
    labels = interpretability_clf.current_view().summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_clf.click(labels[key][model_idx])

    rng = np.random.default_rng(seed=123)
    df = pd.DataFrame(rng.random((6, 2)), columns=['foo', 'bar'])
    df['Pred'] = 2
    df['Proba'] = 0.50
    df['Ground Truth'] = rng.integers(3, size=(6,))

    actual = interpretability_clf.current_view().df[2]  # estimator only predicts label 2.
    expected = df

    pd.testing.assert_frame_equal(actual, expected)


@pytest.fixture
def reg_pipeline():
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

    pipeline.type = 'regression'
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
def interpretability_reg(gui: GuiTestApi, reg_pipeline):
    gui.tabs.setTabEnabled(gui.widget.interpretability_tab_index, True)
    gui.populate_interpretability_tab(reg_pipeline)
    return gui


def test_dataframe_in_model_view_reg(interpretability_reg: GuiTestApi):
    interpretability_reg.tabs.setCurrentIndex(interpretability_reg.widget.interpretability_tab_index)
    labels = interpretability_reg.current_view().summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    interpretability_reg.click(labels[key][model_idx])

    rng = np.random.default_rng(seed=123)
    df = pd.DataFrame(rng.random((6, 2)), columns=['foo', 'bar'])
    df['Pred'] = 2
    df['Ground Truth'] = rng.integers(3, size=(6,))

    actual = interpretability_reg.current_view().df
    expected = df

    pd.testing.assert_frame_equal(actual, expected)
