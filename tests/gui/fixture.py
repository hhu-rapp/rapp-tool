import pytest
from pytestqt.qtbot import QtBot
from PyQt5.QtCore import Qt
from rapp.gui import Window

import tests.resources as rc


@pytest.fixture
def gui(qtbot):
    gui = Window(rc.get_path('test.db'))
    qtbot.addWidget(gui)
    return GuiTestApi(gui, qtbot)


class GuiTestApi():
    """
    Provides easy access to GUI functionalities to write clean tests.
    """

    def __init__(self, widget: Window, qtbot: QtBot):
        self.widget = widget
        self.qtbot = qtbot

        # Setup links to all the window elements for shorter names/convenience.
        self.statusbar = widget.statusbar
        # self.tabs = widget.tabs

        # SQL Field
        self.sql_features_select_box = widget.databaseLayoutWidget.sql_tabs.featuresSelect
        self.sql_target_select_box = widget.databaseLayoutWidget.sql_tabs.targetSelect
        self.sql_template_load_btn = widget.databaseLayoutWidget.sql_tabs.verifySelect

        self.sql_table_box = widget.databaseLayoutWidget.pandasTv.combo

        self.sql_tabs = widget.databaseLayoutWidget.sql_tabs.tabs
        self.sql_text_field = widget.databaseLayoutWidget.sql_tabs.sql_field
        self.execute_sql_btn = widget.databaseLayoutWidget.sql_tabs.qPushButtonExecuteSql
        self.sql_undo_btn = widget.databaseLayoutWidget.sql_tabs.qPushButtonUndoSql
        self.sql_redo_btn = widget.databaseLayoutWidget.sql_tabs.qPushButtonRedoSql

        # Pipeline settings
        self.target_var_box = widget.tabs.MLTab.cbName
        self.categorical_var_field = widget.tabs.MLTab.leCVariables
        self.sensitive_attr_box = widget.tabs.MLTab.cbSAttributes
        self.ml_type_box = widget.tabs.MLTab.cbType
        self.report_path_field = widget.tabs.MLTab.lePath
        self.report_path_btn = widget.tabs.MLTab.reportPathButton
        self.imputation_box = widget.tabs.MLTab.cbImputation
        self.feature_selection_box = widget.tabs.MLTab.cbFSM
        self.estimator_select_box = widget.tabs.MLTab.cbEstimator
        self.train_btn = widget.tabs.MLTab.trainButton

        # Menubar
        self.menubar = widget.menubar
        self.load_cf = lambda file: widget.menubar.loadConfigurationFile(file)

    def get_df(self):
        return self.widget.databaseLayoutWidget.sql_df

    def key_click(self, element, key_sequence, mod=Qt.NoModifier, delay=-1):
        """
        Send key events to the specified GUI element.
        `key_sequence` can either be a single char or a string.
        """
        if len(key_sequence) > 1:
            fun = self.qtbot.keyClicks
        else:
            fun = self.qtbot.keyClick
        fun(element, key_sequence, modifier=mod, delay=delay)

    def key_event(self, element, action, key, mod=Qt.NoModifier, delay=-1):
        self.qtbot.keyEvent(action, element, key, modifier=mod, delay=delay)

    def key_press(self, element, key, mod=Qt.NoModifier, delay=-1):
        self.qtbot.keyPress(element, key, modifier=mod, delay=delay)

    def key_release(self, element, key, mod=Qt.NoModifier, delay=-1):
        self.qtbot.keyRelease(element, key, modifier=mod, delay=delay)

    def click(self, element, btn=Qt.MouseButton.LeftButton, **kwargs):
        """
        Click on the given GUI element.

        Parameters
        ----------
        element :
            GUI-Element to click on.
        btn : Qt.MouseButton flag
        """
        self.qtbot.mouseClick(element, btn, **kwargs)

    def lclick(self, element, **kwargs):
        """
        Left-click on the given GUI element.
        """
        self.click(element, Qt.MouseButton.LeftButton, **kwargs)

    def rclick(self, element, **kwargs):
        """
        Right-click on the given GUI element.
        """
        self.click(element, Qt.MouseButton.RightButton, **kwargs)

    def dclick(self, element, btn=Qt.MouseButton.LeftButton, **kwargs):
        """
        Double-click on the given GUI element.
        """
        self.qtbot.mouseDClick(element, btn, **kwargs)

    def mouse_move(self, element, **kwargs):
        """
        Move mouse over element.
        """
        self.qtbot.mouseMove(element, **kwargs)

    def mouse_press(self, element, btn=Qt.MouseButton.LeftButton, **kwargs):
        """
        Press the mouse button onto the given GUI element.

        Parameters
        ----------
        element :
            GUI-Element to click on.
        btn : Qt.MouseButton flag
        """
        self.qtbot.mousePress(element, btn, **kwargs)

    def mouse_release(self, element, btn=Qt.MouseButton.LeftButton, **kwargs):
        self.qtbot.mousePress(element, btn, **kwargs)

    def wait(self, milliseconds):
        self.qtbot.wait(milliseconds)

    def show(self):
        self.widget.show()
