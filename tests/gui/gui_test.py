from types import SimpleNamespace
import pandas as pd
from sklearn.dummy import DummyClassifier

from rapp import sqlbuilder
from rapp.gui.widgets import DatasetTable, OverviewTable, IndividualPerformanceTable, IndividualFairnessTable

from tests.gui.fixture import gui, GuiTestApi
import tests.resources as rc
from tests.testutil import get_db_connection


def test_select_sql_features(gui: GuiTestApi):
    gui.key_click(gui.sql_features_select_box, "cs_first_term_modules")

    assert gui.sql_features_select_box.currentText() == "cs_first_term_modules"


def test_select_sql_target(gui: GuiTestApi):
    gui.key_click(gui.sql_target_select_box, "3_dropout")

    assert gui.sql_target_select_box.currentText() == "3_dropout"


def test_sql_template_loading(gui: GuiTestApi):
    features_id = "cs_first_term_modules"
    labels_id = "3_dropout"

    gui.key_click(gui.sql_features_select_box, features_id)
    gui.key_click(gui.sql_target_select_box, labels_id)
    gui.click(gui.sql_template_load_btn)

    reference_sql = sqlbuilder.load_sql(features_id, labels_id)
    # Note: Comparing with gui.sql_text_field.toPlainText() fails on weird
    # whitespace issue somehow.
    assert (reference_sql ==
            gui.widget.databaseLayoutWidget.pandasTv.get_custom_sql())


def test_sql_template_loads_df(gui: GuiTestApi):
    features_id = "cs_first_term_modules"
    labels_id = "3_dropout"

    gui.key_click(gui.sql_features_select_box, features_id)
    gui.key_click(gui.sql_target_select_box, labels_id)
    gui.click(gui.sql_template_load_btn)

    reference_sql = sqlbuilder.load_sql(features_id, labels_id)

    conn = get_db_connection()
    expected_df = pd.read_sql_query(reference_sql, conn)

    assert gui.get_df().equals(expected_df)


def test_loading_config_file(gui: GuiTestApi, tmp_path):
    # As the config file needs to list a database path and we
    # want to use the test database, we copy the sample file into
    # a temporary directory and add the required line
    cf = tmp_path / 'config.ini'
    cf_text = rc.get_text('sql_template_sample.ini')
    cf_text += f"\nfilename=\"{rc.get_path('test.db')}\""
    cf.write_text(cf_text)
    gui.load_cf(cf)

    # Check whether
    errors = []

    if gui.sql_features_select_box.currentText() != "cs_first_term_modules":
        errors.append("Feature template id not set correctly")
    if gui.sql_target_select_box.currentText() != "3_dropout":
        errors.append("Feature template id not set correctly")

    if gui.target_var_box.currentText() != "Dropout":
        errors.append(f"target variable is '{gui.target_var_box.currentText()}'"
                      f" instead of 'Dropout'")
    if gui.categorical_var_field.text() != "Geschlecht":
        errors.append("Categorical variables set as"
                      f" '{gui.categorical_var_field.text()}'"
                      " instead of 'Geschlecht'")
    if gui.sensitive_attr_box.get_checked_items() != ["Geschlecht", "Deutsch"]:
        errors.append("Sensitive Attributes not correctly set:"
                      f" is '{gui.sensitive_attr_box.get_checked_items()}'"
                      f" instead of 'Geschlecht' and 'Deutsch'")
    if gui.estimator_select_box.get_checked_items() != ["DT"]:
        errors.append("Estimator selection should only be DT"
                      f" but is {gui.estimator_select_box.get_checked_items()}")
    if gui.ml_type_box.currentText() != 'Classification':
        errors.append("Prediction type should be 'Classification'"
                      f" but is {gui.ml_type_box.currentText()}")

    assert not errors, "\n".join(errors)


def test_selecting_template_label_selects_prediction_type(gui: GuiTestApi):
    features_id = "cs_first_term_modules"
    labels_id = [gui.sql_target_select_box.itemText(i) for i in range(gui.sql_target_select_box.count())]
    # Check whether
    errors = []

    for label in labels_id:

        if len(label) == 0:
            continue

        gui.key_click(gui.sql_features_select_box, features_id)
        gui.key_click(gui.sql_target_select_box, label)
        gui.click(gui.sql_template_load_btn)

        df = gui.get_df()

        unique_label_count = len(df[gui.target_var_box.currentText()].unique())
        total_label_count = len(df[gui.target_var_box.currentText()])
        unique_label_ratio = unique_label_count / total_label_count

        if unique_label_ratio > 0.5:
            expected_type = 'Regression'
        else:
            expected_type = 'Classification'

        if gui.ml_type_box.currentText() != expected_type:
            errors.append(f"{gui.target_var_box.currentText()} unique label ratio is {unique_label_ratio}"
                          f" prediction type should be {expected_type}"
                          f" but is {gui.ml_type_box.currentText()}")

    assert not errors, "\n".join(errors)


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
    assert actual == expected,\
        f"The Number of collapsible boxes in the dataset tab should be {actual}, but is {expected}"

    actual = type(gui.dataset_tables[0])
    expected = DatasetTable
    assert actual == expected,\
        f"The type of widget in the dataset tab should be {actual}, but is {expected}"

    # Tests for Overview Tab
    actual = gui.overview_performance_metrics_selection_box.get_checked_items()
    expected = ['A', 'B']
    assert actual == expected,\
        f"The performance metrics selection box in the overview tab should be {actual}, but is {expected}"

    actual = gui.overview_fairness_metrics_selection_box.get_checked_items()
    expected = ['C']
    assert actual == expected,\
        f"The fairness metrics selection box in the overview tab should be {actual}, but is {expected}"

    actual = [gui.overview_modes_selection_box.itemText(i) for i in range(gui.overview_modes_selection_box.count())]
    expected = ['Train']
    assert actual == expected,\
        f"The mode selection box in the overview tab should be {actual}, but is {expected}"

    actual = [gui.overview_sensitive_selection_box.itemText(i) for i in
              range(gui.overview_sensitive_selection_box.count())]
    expected = ['Sensitive', 'Protected']
    assert actual == expected,\
        f"The sensitive selection box in the overview tab should be {actual}, but is {expected}"

    actual = type(gui.overview_table)
    expected = OverviewTable
    assert actual == expected,\
        f"The type of widget in the overview tab should be {actual}, but is {expected}"

    # Tests for Individual Tab
    actual = [gui.individual_model_selection_box.itemText(i) for i in range(gui.individual_model_selection_box.count())]
    expected = ['DummyClassifier', 'DummyClassifier']
    assert actual == expected,\
        f"The model selection box in the individual tab should be {actual}, but is {expected}"

    actual = type(gui.individual_performance_table)
    expected = IndividualPerformanceTable
    assert actual == expected,\
        f"The type of widget in the overview tab should be {actual}, but is {expected}"

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
