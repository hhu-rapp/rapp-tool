from PyQt5.QtWidgets import QTabBar
from PyQt5 import QtTest

from fixture import gui, GuiTestApi


def test_selection_in_combo_box(gui: GuiTestApi):
    assert gui.sql_features_select_box.currentIndex() == 0

    gui.key_click(gui.sql_features_select_box, 'cs_first_term_grades')

    expected = 1
    actual = gui.sql_features_select_box.currentIndex()

    assert expected == actual
