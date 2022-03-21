import pandas as pd
from PyQt5.QtCore import Qt

from rapp import sqlbuilder
from rapp.gui import Window

import tests.resources as rc
from tests.testutil import get_db_connection


def test_select_sql_features(qtbot):
    gui = Window()
    qtbot.addWidget(gui)

    qtbot.keyClicks(gui.databaseLayoutWidget.sql_tabs.featuresSelect,
                    "cs_first_term_modules")

    assert (gui.databaseLayoutWidget.sql_tabs.featuresSelect.currentText() ==
            "cs_first_term_modules")


def test_select_sql_target(qtbot):
    gui = Window()
    qtbot.addWidget(gui)

    qtbot.keyClicks(gui.databaseLayoutWidget.sql_tabs.targetSelect,
                    "3_dropout")

    assert (gui.databaseLayoutWidget.sql_tabs.targetSelect.currentText() ==
            "3_dropout")


def test_sql_template_loading(qtbot):
    gui = Window()
    qtbot.addWidget(gui)

    features_id = "cs_first_term_modules"
    labels_id = "3_dropout"

    qtbot.keyClicks(gui.databaseLayoutWidget.sql_tabs.featuresSelect,
                    features_id)
    qtbot.keyClicks(gui.databaseLayoutWidget.sql_tabs.targetSelect,
                    labels_id)
    qtbot.mouseClick(gui.databaseLayoutWidget.sql_tabs.verifySelect,
                     Qt.MouseButton.LeftButton)

    sql = sqlbuilder.load_sql(features_id, labels_id)
    assert sql == gui.databaseLayoutWidget.pandasTv.get_custom_sql()


def test_sql_template_loads_df(qtbot):
    gui = Window(rc.get_path('test.db'))
    qtbot.addWidget(gui)

    features_id = "cs_first_term_modules"
    labels_id = "3_dropout"

    qtbot.keyClicks(gui.databaseLayoutWidget.sql_tabs.featuresSelect,
                    features_id)
    qtbot.keyClicks(gui.databaseLayoutWidget.sql_tabs.targetSelect,
                    labels_id)
    qtbot.mouseClick(gui.databaseLayoutWidget.sql_tabs.verifySelect,
                     Qt.MouseButton.LeftButton)

    reference_sql = sqlbuilder.load_sql(features_id, labels_id)

    conn = get_db_connection()
    expected_df = pd.read_sql_query(reference_sql, conn)

    assert gui.databaseLayoutWidget.sql_df.equals(expected_df)
