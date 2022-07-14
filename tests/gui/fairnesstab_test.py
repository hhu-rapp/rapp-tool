from types import SimpleNamespace

import pytest
from sklearn.dummy import DummyClassifier
from rapp.gui.widgets import DatasetTables, OverviewTable, IndividualPerformanceTable, IndividualFairnessTable, \
    DatasetTable

from tests.gui.fixture import gui, GuiTestApi


@pytest.fixture
def clf_pipeline():
    est1 = DummyClassifier()
    est2 = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.estimators = [est1, est2]
    pipeline.data = {'train': None}
    pipeline.statistics_results = {'train': {'groups':
                                                 {'Sensitive': {'foo': {'total': 10,
                                                                        'outcomes': {0: 6,
                                                                                     1: 4,
                                                                                     }}},
                                                  'Protected': {'bar': {'total': 10,
                                                                        'outcomes': {0: 5,
                                                                                     1: 5,
                                                                                     }},
                                                                'baz': {'total': 10,
                                                                        'outcomes': {0: 6,
                                                                                     1: 4,
                                                                                     }}
                                                                }},
                                             'outcomes': {0: 11, 1: 9},
                                             'total': 20}}
    pipeline.sensitive_attributes = ['Sensitive', 'Protected']
    pipeline.type = 'classification'
    pipeline.score_functions = {'A': None,
                                'B': None}
    pipeline.fairness_functions = {'C': None}

    pipeline.performance_results = {est1: {
        'train': {
            'scores': {
                'A': 0.2,
                'B': 0.5},
            'confusion_matrix': [[0, 8], [0, 2]]}}}
    pipeline.performance_results[est2] = pipeline.performance_results[est1]

    pipeline.fairness_results = {est1: {'Sensitive':
                                            {'C': {'train': {'foo': {'affected_percent': 0.5,
                                                                     'confusion_matrix': [0, 2, 4, 7]}}}},
                                        'Protected':
                                            {'C': {'train': {'bar': {'affected_percent': 0.5,
                                                                     'confusion_matrix': [0, 2, 4, 7]},
                                                             'baz': {'affected_percent': 0.5,
                                                                     'confusion_matrix': [0, 4, 4, 3]}}}}}}
    pipeline.fairness_results[est2] = pipeline.fairness_results[est1]

    return pipeline


@pytest.fixture
def clf_settings():
    return {'studies_id': 'cs',
            'features_id': 'first_term_ects',
            'labels_id': '3_dropout'}


@pytest.fixture
def fairtab_clf(gui: GuiTestApi, clf_pipeline, clf_settings):
    gui.tabs.setTabEnabled(gui.widget.fairness_tab_index, True)
    gui.populate_fairness_tabs(clf_pipeline, clf_settings)
    return gui


def test_collapsible_num(fairtab_clf: GuiTestApi):
    actual = len(fairtab_clf.dataset_tables)
    expected = 2
    assert actual == expected, \
        f"The Number of collapsible boxes in the dataset tab should be {expected}, but is {actual}"


def test_datatab_widget_type(fairtab_clf: GuiTestApi):
    sensitive = 'Protected'  # only test second sensitive attribute

    actual = type(fairtab_clf.dataset_tables[sensitive])
    expected = DatasetTable
    assert actual == expected, \
        f"The type of widget in the dataset tab should be {expected}, but is {actual}"


def test_performance_metrics_selection(fairtab_clf: GuiTestApi):
    actual = fairtab_clf.overview_performance_metrics_selection_box.get_checked_items()
    expected = ['A', 'B']
    assert actual == expected, \
        f"The performance metrics selection box in the overview tab should be {expected}, but is {actual}"


def test_fairness_metrics_selection(fairtab_clf: GuiTestApi):
    actual = fairtab_clf.overview_fairness_metrics_selection_box.get_checked_items()
    expected = ['C']
    assert actual == expected, \
        f"The fairness metrics selection box in the overview tab should be {expected}, but is {actual}"


def test_default_mode_selection_value(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.overview_modes_selection_box.itemText(
        i) for i in range(fairtab_clf.overview_modes_selection_box.count())]
    expected = ['Train']
    assert actual == expected, \
        f"The mode selection box in the overview tab should be {expected}, but is {actual}"


def test_protected_attr_default_selection_value(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.overview_sensitive_selection_box.itemText(i) for i in
              range(fairtab_clf.overview_sensitive_selection_box.count())]
    expected = ['Sensitive', 'Protected']
    assert actual == expected, \
        f"The sensitive selection box in the overview tab should be {expected}, but is {actual}"


def test_widget_type_in_overview(fairtab_clf: GuiTestApi):
    actual = type(fairtab_clf.overview_table)
    expected = OverviewTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"


def test_listed_models_in_model_inspection(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.individual_model_selection_box.itemText(i)
              for i in range(
            fairtab_clf.individual_model_selection_box.count())]
    expected = ['DummyClassifier', 'DummyClassifier']
    assert actual == expected, \
        f"The model selection box in the individual tab should be {expected}, but is {actual}"


def test_widget_type_of_individual_performance_table(fairtab_clf: GuiTestApi):
    actual = type(fairtab_clf.individual_performance_table)
    expected = IndividualPerformanceTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"


def test_select_individual_fairness_metric(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.fairness_tab_index)
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.fairness.individual_tab_idx)

    fairtab_clf.key_click(fairtab_clf.individual_metrics_selection_box,
                          'Fairness')

    actual = len(fairtab_clf.get_individual_fairness_tables())
    expected = 2
    assert actual == expected, \
        f"The Number of collapsible boxes in the individual tab should be {expected}, but is {actual}"


def test_individual_fairness_table_type(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.fairness_tab_index)
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.fairness.individual_tab_idx)
    fairtab_clf.key_click(
        fairtab_clf.individual_metrics_selection_box, "Fairness")
    actual = type(fairtab_clf.get_individual_fairness_tables()['Protected'])
    expected = IndividualFairnessTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"


def test_click_on_model_in_overview(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.fairness_tab_index)
    labels = fairtab_clf.overview_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.fairness.overview_tab_idx)
    fairtab_clf.click(labels[key][model_idx])

    actual = fairtab_clf.fairness_tabs.currentIndex()
    expected = fairtab_clf.widget.fairness.individual_tab_idx
    assert actual == expected, \
        f"The fairness tab index should have changed to {expected}, but is {actual}"


def test_click_on_model_in_overview2(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.fairness_tab_index)
    labels = fairtab_clf.overview_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.fairness.overview_tab_idx)
    fairtab_clf.click(labels[key][model_idx])

    actual = fairtab_clf.individual_model_selection_box.currentIndex()
    expected = model_idx
    assert actual == expected, \
        f"The modelComboBo's index should be {expected}, but is {actual}"
