import pandas as pd

from rapp import sqlbuilder

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
