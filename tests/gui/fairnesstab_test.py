from types import SimpleNamespace

from sklearn.dummy import DummyClassifier

from rapp.gui.widgets import DatasetTable, OverviewTable, IndividualPerformanceTable, IndividualFairnessTable

from tests.gui.fixture import gui, GuiTestApi


def test_fairness_tabs_classification(gui: GuiTestApi):
    est1 = DummyClassifier()
    est2 = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.data = {'train': None}
    pipeline.statistics_results = {'train': {'groups':
                                                 {'Sensitive': {'foo': {'total': 10,
                                                                        'outcomes': {0: 6,
                                                                                     1: 4,
                                                                                     }}},
                                                  'Protected': {'bar': {'total': 10,
                                                                        'outcomes': {0: 5,
                                                                                     1: 5,
                                                                                     }}}},
                                             'outcomes': {0: 11, 1: 9},
                                             'total': 20}}
    pipeline.sensitive_attributes = ['Sensitive', 'Protected']
    pipeline.type = 'classification'
    data_settings = {'studies_id': 'cs',
                     'features_id': 'first_term_ects',
                     'labels_id': '3_dropout'}
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
                                                                     'confusion_matrix': [0, 2, 4, 7]}}}}}}
    pipeline.fairness_results[est2] = pipeline.fairness_results[est1]

    gui.populate_fairness_tabs(pipeline, data_settings)

    # Tests for Dataset Tab
    actual = len(gui.dataset_tables)
    expected = 2
    assert actual == expected, \
        f"The Number of collapsible boxes in the dataset tab should be {expected}, but is {actual}"

    actual = type(gui.dataset_tables[0])
    expected = DatasetTable
    assert actual == expected, \
        f"The type of widget in the dataset tab should be {expected}, but is {actual}"

    # Tests for Overview Tab
    actual = gui.overview_performance_metrics_selection_box.get_checked_items()
    expected = ['A', 'B']
    assert actual == expected, \
        f"The performance metrics selection box in the overview tab should be {expected}, but is {actual}"

    actual = gui.overview_fairness_metrics_selection_box.get_checked_items()
    expected = ['C']
    assert actual == expected, \
        f"The fairness metrics selection box in the overview tab should be {expected}, but is {actual}"

    actual = [gui.overview_modes_selection_box.itemText(i) for i in range(gui.overview_modes_selection_box.count())]
    expected = ['Train']
    assert actual == expected, \
        f"The mode selection box in the overview tab should be {expected}, but is {actual}"

    actual = [gui.overview_sensitive_selection_box.itemText(i) for i in
              range(gui.overview_sensitive_selection_box.count())]
    expected = ['Sensitive', 'Protected']
    assert actual == expected, \
        f"The sensitive selection box in the overview tab should be {expected}, but is {actual}"

    actual = type(gui.overview_table)
    expected = OverviewTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"

    # Tests for Individual Tab
    actual = [gui.individual_model_selection_box.itemText(i) for i in range(gui.individual_model_selection_box.count())]
    expected = ['DummyClassifier', 'DummyClassifier']
    assert actual == expected, \
        f"The model selection box in the individual tab should be {expected}, but is {actual}"

    actual = type(gui.individual_performance_table)
    expected = IndividualPerformanceTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"

    # FIXME: individual_metrics_selection_box is not updating
    # gui.tabs.setCurrentIndex(gui.widget.fairness_tab_index)
    # gui.fairness_tabs.setCurrentIndex(gui.widget.fairness.individual_tab_idx)
    # gui.key_click(gui.individual_metrics_selection_box, "Fairness")
    # actual = len(gui.individual_fairness_tables)
    # expected = 2
    # assert actual == expected,\
    #     f"The Number of collapsible boxes in the individual tab should be {actual}, but is {expected}"
    #
    # actual = type(gui.individual_fairness_tables[0])
    # expected = IndividualFairnessTable
    # assert actual == expected,\
    # f"The type of widget in the overview tab should be {actual}, but is {expected}"
    # FIXME: clicking on the model's label does not seem to work
    # gui.tabs.setCurrentIndex(gui.widget.fairness_tab_index)
    # for model_idx in range(len([est1, est2])):
    #     gui.fairness_tabs.setCurrentIndex(gui.widget.fairness.overview_tab_idx)
    #     gui.click(gui.overview_table.labelModels[model_idx])
    #
    #     actual = gui.fairness_tabs.currentIndex()
    #     expected = gui.widget.fairness.individual_tab_idx
    #     assert actual == expected,\
    #     f"The fairness tab index should have changed to {expected}, but is {actual}"
    #
    #     actual = gui.individual_model_selection_box.currentIndex()
    #     expected = model_idx
    #     assert actual == expected,\
    #     f"The modelComboBo's index should be {expected}, but is {actual}"


def test_fairness_tabs_regression(gui: GuiTestApi):
    est1 = DummyClassifier()
    est2 = DummyClassifier()

    pipeline = SimpleNamespace()
    pipeline.data = {'train': None}
    pipeline.statistics_results = {'train': {'groups':
                                                 {'Sensitive': {'foo': {'total': 10,
                                                                        'outcomes': {0: 6,
                                                                                     1: 4,
                                                                                     }}},
                                                  'Protected': {'bar': {'total': 10,
                                                                        'outcomes': {0: 5,
                                                                                     1: 5,
                                                                                     }}}},
                                             'outcomes': {0: 11, 1: 9},
                                             'total': 20}}
    pipeline.sensitive_attributes = ['Sensitive', 'Protected']
    pipeline.type = 'regression'
    data_settings = {'studies_id': 'cs',
                     'features_id': 'first_term_ects',
                     'labels_id': '3_dropout'}
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

    gui.populate_fairness_tabs(pipeline, data_settings)

    # Tests for Dataset Tab
    actual = len(gui.dataset_tables)
    expected = 2
    assert actual == expected, \
        f"The Number of collapsible boxes in the dataset tab should be {expected}, but is {actual}"

    actual = type(gui.dataset_tables[0])
    expected = DatasetTable
    assert actual == expected, \
        f"The type of widget in the dataset tab should be {expected}, but is {actual}"

    # Tests for Overview Tab
    actual = gui.overview_performance_metrics_selection_box.get_checked_items()
    expected = ['A', 'B']
    assert actual == expected, \
        f"The performance metrics selection box in the overview tab should be {expected}, but is {actual}"

    actual = gui.overview_fairness_metrics_selection_box.get_checked_items()
    expected = ['C']
    assert actual == expected, \
        f"The fairness metrics selection box in the overview tab should be {expected}, but is {actual}"

    actual = [gui.overview_modes_selection_box.itemText(i) for i in range(gui.overview_modes_selection_box.count())]
    expected = ['Train']
    assert actual == expected, \
        f"The mode selection box in the overview tab should be {expected}, but is {actual}"

    actual = [gui.overview_sensitive_selection_box.itemText(i) for i in
              range(gui.overview_sensitive_selection_box.count())]
    expected = ['Sensitive', 'Protected']
    assert actual == expected, \
        f"The sensitive selection box in the overview tab should be {expected}, but is {actual}"

    actual = type(gui.overview_table)
    expected = OverviewTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"

    # Tests for Individual Tab
    actual = [gui.individual_model_selection_box.itemText(i) for i in range(gui.individual_model_selection_box.count())]
    expected = ['DummyClassifier', 'DummyClassifier']
    assert actual == expected, \
        f"The model selection box in the individual tab should be {expected}, but is {actual}"

    actual = type(gui.individual_performance_table)
    expected = IndividualPerformanceTable
    assert actual == expected, \
        f"The type of widget in the overview tab should be {expected}, but is {actual}"

    # FIXME: individual_metrics_selection_box is not updating
    # gui.key_click(gui.individual_metrics_selection_box, "Fairness")
    # actual = len(gui.individual_fairness_tables)
    # expected = 2
    # assert actual == expected,\
    #     f"The Number of collapsible boxes in the individual tab should be {actual}, but is {expected}"
    #
    # actual = type(gui.individual_fairness_tables[0])
    # expected = IndividualFairnessTable
    # assert actual == expected,\
    # f"The type of widget in the overview tab should be {actual}, but is {expected}"
    # FIXME: clicking on the model's label does not seem to work
    # gui.tabs.setCurrentIndex(gui.widget.fairness_tab_index)
    # for model_idx in range(len([est1, est2])):
    #     gui.fairness_tabs.setCurrentIndex(gui.widget.fairness.overview_tab_idx)
    #     gui.click(gui.overview_table.labelModels[model_idx])
    #
    #     actual = gui.fairness_tabs.currentIndex()
    #     expected = gui.widget.fairness.individual_tab_idx
    #     assert actual == expected,\
    #     f"The fairness tab index should have changed to {expected}, but is {actual}"
    #
    #     actual = gui.individual_model_selection_box.currentIndex()
    #     expected = model_idx
    #     assert actual == expected,\
    #     f"The modelComboBo's index should be {expected}, but is {actual}"
