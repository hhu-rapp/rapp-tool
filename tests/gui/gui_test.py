import pandas as pd

from rapp import sqlbuilder

from tests.gui.fixture import gui, GuiTestApi
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
