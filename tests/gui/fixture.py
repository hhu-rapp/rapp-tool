import pytest

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

    def __init__(self, gui : Window, qtbot):
        self.widget = gui
        self.qtbot = qtbot

        # Setup links to all the window elements for shorter names/convenience.
        self.statusbar = gui.statusbar
        # self.tabs = gui.tabs

        ## SQL Field
        self.sql_features_select_box = gui.databaseLayoutWidget.sql_tabs.featuresSelect
        self.sql_target_select_box = gui.databaseLayoutWidget.sql_tabs.targetSelect
        self.sql_template_load_btn = gui.databaseLayoutWidget.sql_tabs.verifySelect

        self.sql_table_box = gui.databaseLayoutWidget.pandasTv.combo

        self.sql_tabs = gui.databaseLayoutWidget.sql_tabs.tabs
        self.sql_text_field = gui.databaseLayoutWidget.sql_tabs.sql_field
        self.execute_sql_btn = gui.databaseLayoutWidget.sql_tabs.qPushButtonExecuteSql
        self.sql_undo_btn = gui.databaseLayoutWidget.sql_tabs.qPushButtonUndoSql
        self.sql_redo_btn = gui.databaseLayoutWidget.sql_tabs.qPushButtonRedoSql

        ## Pipeline settings
        self.target_var_box = gui.tabs.MLTab.cbName
        self.categorical_var_field = gui.tabs.MLTab.leCVariables
        self.sensitive_attr_box = gui.tabs.MLTab.cbSAttributes
        self.ml_type_box = gui.tabs.MLTab.cbType
        self.report_path_field = gui.tabs.MLTab.lePath
        self.report_path_btn = gui.tabs.MLTab.reportPathButton
        self.imputation_box = gui.tabs.MLTab.cbImputation
        self.feature_selection_box = gui.tabs.MLTab.cbFSM
        self.estimator_select_box = gui.tabs.MLTab.cbEstimator
        self.train_btn = gui.tabs.MLTab.trainButton

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
