from types import SimpleNamespace

import numpy as np
import pytest
from sklearn.dummy import DummyClassifier
from rapp.gui.widgets import DatasetTables, SummaryTable, InspectionPerformanceTable, InspectionFairnessCollapsible, \
    DatasetTable, ParetoCollapsible, ParetoPlot, DatasetPlot

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
    gui.tabs.setTabEnabled(gui.widget.evaluation_tab_index, True)
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
    expected = DatasetTables
    assert actual == expected, \
        f"The type of widget in the dataset tab should be {expected}, but is {actual}"


def test_clf_datatable_widget_type(fairtab_clf: GuiTestApi):
    sensitive = 'Protected'  # only test second sensitive attribute
    mode = 'train'

    actual = type(fairtab_clf.dataset_tables[sensitive].dataset_groupBox[mode])
    expected = DatasetTable
    assert actual == expected, \
        f"The type of widget in the dataset tab should be {expected}, but is {actual}"


def test_dataset_table(fairtab_clf: GuiTestApi):
    sensitive = 'Protected'  # only test second sensitive attribute
    mode = 'train'

    labels = fairtab_clf.dataset_tables[sensitive].dataset_groupBox[mode].labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Class': ['0', '1', 'Total'],
                'Bar': ['5', '5', '10'],
                'Baz': ['6', '4', '10'],
                'Total': ['11', '9', '20']}
    assert actual == expected, \
        f"The values in the dataset table should be {expected}, but are {actual}"


def test_performance_metrics_selection(fairtab_clf: GuiTestApi):
    actual = fairtab_clf.summary_performance_metrics_selection_box.get_checked_items()
    expected = ['A', 'B']
    assert actual == expected, \
        f"The performance metrics selection box in the summary tab should be {expected}, but is {actual}"


def test_fairness_metrics_selection(fairtab_clf: GuiTestApi):
    actual = fairtab_clf.summary_fairness_metrics_selection_box.get_checked_items()
    expected = ['C']
    assert actual == expected, \
        f"The fairness metrics selection box in the summary tab should be {expected}, but is {actual}"


def test_default_mode_selection_value(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.summary_modes_selection_box.itemText(
        i) for i in range(fairtab_clf.summary_modes_selection_box.count())]
    expected = ['Train']
    assert actual == expected, \
        f"The mode selection box in the summary tab should be {expected}, but is {actual}"


def test_protected_attr_default_selection_value(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.summary_sensitive_selection_box.itemText(i) for i in
              range(fairtab_clf.summary_sensitive_selection_box.count())]
    expected = ['Sensitive', 'Protected']
    assert actual == expected, \
        f"The sensitive selection box in the summary tab should be {expected}, but is {actual}"


def test_widget_type_in_summary(fairtab_clf: GuiTestApi):
    actual = type(fairtab_clf.summary_table)
    expected = SummaryTable
    assert actual == expected, \
        f"The type of widget in the summary tab should be {expected}, but is {actual}"


def test_table_in_summary(fairtab_clf: GuiTestApi):
    labels = fairtab_clf.summary_table.labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Model': ['DummyClassifier', 'DummyClassifier'],
                'A': ['0.200', '0.200'],
                'B': ['0.500', '0.500'],
                'C': ['0.500', '0.500']}
    assert actual == expected, \
        f"The values in the summary table should be {expected}, but are {actual}"


def test_listed_models_in_model_inspection(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.model_inspection_selection_box.itemText(i)
              for i in range(
            fairtab_clf.model_inspection_selection_box.count())]
    expected = ['DummyClassifier', 'DummyClassifier']
    assert actual == expected, \
        f"The model selection box in the inspection tab should be {expected}, but is {actual}"


def test_widget_type_of_inspection_performance_table(fairtab_clf: GuiTestApi):
    actual = type(fairtab_clf.inspection_performance_table)
    expected = InspectionPerformanceTable
    assert actual == expected, \
        f"The type of widget in the inspection tab should be {expected}, but is {actual}"


def test_cm_table(fairtab_clf: GuiTestApi):
    mode = 'train'
    labels = fairtab_clf.cm_table[mode].labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Class': ['0', '1'],
                '0': ['0', '0'],
                '1': ['8', '2']}

    assert actual == expected, \
        f"The values in the confusion matrix table should be {expected}, but is {actual}"


def test_perfomance_metrics_table(fairtab_clf: GuiTestApi):
    mode = 'train'
    labels = fairtab_clf.metrics_table[mode].labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Metric': ['A', 'B'],
                'Value': ['0.200', '0.500']}

    assert actual == expected, \
        f"The values in the performance metrics table should be {expected}, but is {actual}"


def test_select_inspection_fairness_metric(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.evaluation_tab_index)
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.evaluation.inspection_tab_idx)

    fairtab_clf.key_click(fairtab_clf.inspection_metrics_selection_box,
                          'Fairness')

    actual = len(fairtab_clf.get_inspection_fairness_tables())
    expected = 2
    assert actual == expected, \
        f"The Number of collapsible boxes in the inspection tab should be {expected}, but is {actual}"


def test_inspection_fairness_table_type(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.evaluation_tab_index)
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.evaluation.inspection_tab_idx)
    fairtab_clf.key_click(
        fairtab_clf.inspection_metrics_selection_box, "Fairness")
    actual = type(fairtab_clf.get_inspection_fairness_tables()['Protected'])
    expected = InspectionFairnessCollapsible
    assert actual == expected, \
        f"The type of widget in the model inspection tab should be {expected}, but is {actual}"


def test_contingency_table(fairtab_clf: GuiTestApi):
    fairtab_clf.key_click(
        fairtab_clf.inspection_metrics_selection_box, "Fairness")

    mode = 'train'
    sensitive = 'Protected'
    labels = fairtab_clf.get_ct_table(sensitive)[mode].labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Class': ['0', '1'],
                'Bar': ['4', '9'],
                'Baz': ['4', '7']
                }

    assert actual == expected, \
        f"The values in the contingency table should be {expected}, but is {actual}"


def test_clf_fairness_notions_table(fairtab_clf: GuiTestApi):
    fairtab_clf.key_click(
        fairtab_clf.inspection_metrics_selection_box, "Fairness")

    mode = 'train'
    sensitive = 'Protected'
    labels = fairtab_clf.get_notions_table(sensitive)[mode].labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Metric': ['C'],
                'Bar': ['0.500'],
                'Baz': ['0.500']}

    assert actual == expected, \
        f"The values in the fairness metrics table should be {expected}, but is {actual}"


def test_click_on_model_in_summary(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.evaluation_tab_index)
    labels = fairtab_clf.summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.evaluation.summary_tab_idx)
    fairtab_clf.click(labels[key][model_idx])

    actual = fairtab_clf.fairness_tabs.currentIndex()
    expected = fairtab_clf.widget.evaluation.inspection_tab_idx
    assert actual == expected, \
        f"The fairness tab index should have changed to {expected}, but is {actual}"


def test_click_on_model_in_summary2(fairtab_clf: GuiTestApi):
    fairtab_clf.tabs.setCurrentIndex(fairtab_clf.widget.evaluation_tab_index)
    labels = fairtab_clf.summary_table.labels

    key = list(labels.keys())[0]  # Key where models are saved
    model_idx = 1  # Only test second model.
    fairtab_clf.fairness_tabs.setCurrentIndex(
        fairtab_clf.widget.evaluation.summary_tab_idx)
    fairtab_clf.click(labels[key][model_idx])

    actual = fairtab_clf.model_inspection_selection_box.currentIndex()
    expected = model_idx
    assert actual == expected, \
        f"The modelComboBo's index should be {expected}, but is {actual}"


def test_listed_metrics_in_pareto_tab(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.pareto_metrics_selection_box.itemText(i)
              for i in range(
            fairtab_clf.pareto_metrics_selection_box.count())]
    expected = ['A', 'B']
    assert actual == expected, \
        f"The metric selection box in the pareto tab should be {expected}, but is {actual}"


def test_listed_notions_in_pareto_tab(fairtab_clf: GuiTestApi):
    actual = [fairtab_clf.pareto_notions_selection_box.itemText(i)
              for i in range(
            fairtab_clf.pareto_notions_selection_box.count())]
    expected = ['C']
    assert actual == expected, \
        f"The notion selection box in the pareto tab should be {expected}, but is {actual}"


def test_pareto_collapsible_num(fairtab_clf: GuiTestApi):
    actual = len(fairtab_clf.pareto_collapsibles)
    expected = 2
    assert actual == expected, \
        f"The number of collapsible boxes in the pareto tab should be {expected}, but is {actual}"


def test_widget_type_of_pareto_collapsible(fairtab_clf: GuiTestApi):
    sensitive = 'Protected'
    actual = type(fairtab_clf.pareto_collapsibles[sensitive])
    expected = ParetoCollapsible
    assert actual == expected, \
        f"The type of widget in the pareto tab should be {expected}, but is {actual}"


def test_widget_type_of_pareto_plot(fairtab_clf: GuiTestApi):
    sensitive = 'Protected'
    mode = 'train'
    actual = type(fairtab_clf.pareto_collapsibles[sensitive].pareto_groupBox[mode])
    expected = ParetoPlot
    assert actual == expected, \
        f"The type of widget in the pareto collapsible tab should be {expected}, but is {actual}"


def test_costs_in_pareto_plot(fairtab_clf: GuiTestApi):
    sensitive = 'Protected'
    mode = 'train'
    actual = fairtab_clf.pareto_collapsibles[sensitive].pareto_groupBox[mode].costs
    expected = np.array([0, 0.2])
    assert (actual == expected).all(), \
        f"The costs for the pareto plot should be {expected}, but is {actual}"


@pytest.fixture
def reg_pipeline():
    est1 = DummyClassifier()
    est2 = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.estimators = [est1, est2]
    pipeline.data = {'train': None}
    pipeline.statistics_results = {'train': {'groups':
                                                 {'Sensitive': {'foo': {'total': 3,
                                                                        'outcomes': np.arange(0, 3)
                                                                        }},
                                                  'Protected': {'bar': {'total': 3,
                                                                        'outcomes': np.arange(3, 6)
                                                                        },
                                                                'baz': {'total': 3,
                                                                        'outcomes': np.arange(6, 9)
                                                                        }
                                                                }},
                                             'outcomes': np.arange(0, 9),
                                             'total': 9}}
    pipeline.sensitive_attributes = ['Sensitive', 'Protected']
    pipeline.type = 'regression'
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
                                            {'C': {'train': 0.5,
                                                   }},
                                        'Protected':
                                            {'C': {'train': 0.5,
                                                   }}}}

    pipeline.fairness_results[est2] = pipeline.fairness_results[est1]

    return pipeline


@pytest.fixture
def reg_settings():
    return {'studies_id': 'cs',
            'features_id': 'first_term_ects',
            'labels_id': 'reg_final_grade'}


@pytest.fixture
def fairtab_reg(gui: GuiTestApi, reg_pipeline, reg_settings):
    gui.tabs.setTabEnabled(gui.widget.evaluation_tab_index, True)
    gui.populate_fairness_tabs(reg_pipeline, reg_settings)
    return gui


def test_reg_datatable_widget_type(fairtab_reg: GuiTestApi):
    sensitive = 'Protected'  # only test second sensitive attribute
    mode = 'train'

    actual = type(fairtab_reg.dataset_tables[sensitive].dataset_groupBox[mode])
    expected = DatasetPlot
    assert actual == expected, \
        f"The type of widget in the dataset tab should be {expected}, but is {actual}"


def test_reg_fairness_notions_table(fairtab_reg: GuiTestApi):
    fairtab_reg.key_click(
        fairtab_reg.inspection_metrics_selection_box, "Fairness")

    mode = 'train'
    sensitive = 'Protected'
    labels = fairtab_reg.get_notions_table(sensitive)[mode].labels

    values = {}
    for label in labels:
        key = label.text()
        values[key] = []
        for val in labels[label]:
            values[key].append(val.text())

    actual = values
    expected = {'Metric': ['C'],
                'Value': ['0.500']}

    assert actual == expected, \
        f"The values in the fairness metrics table should be {expected}, but is {actual}"
