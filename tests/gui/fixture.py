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
        self.tabs = widget.tabs

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
        self.target_var_box = widget.settings.simple_tab.cbName
        self.categorical_var_field = widget.settings.simple_tab.leCVariables
        self.sensitive_attr_box = widget.settings.simple_tab.cbSAttributes
        self.ml_type_box = widget.settings.simple_tab.cbType
        self.report_path_field = widget.settings.simple_tab.lePath
        self.report_path_btn = widget.settings.simple_tab.reportPathButton
        self.imputation_box = widget.settings.simple_tab.cbImputation
        self.feature_selection_box = widget.settings.simple_tab.cbFSM
        self.estimator_select_box = widget.settings.simple_tab.cbEstimator
        self.train_btn = widget.settings.simple_tab.trainButton

        # Menubar
        self.menubar = widget.menubar
        self.load_cf = lambda file: widget.menubar.loadConfigurationFile(file)

        # Fairness Tab
        self.fairness_tabs = widget.fairness.tabs
        self.populate_fairness_tabs = lambda pl, data_settings: self._populate_fairness_tabs(widget, pl, data_settings)
        # Dataset Tab
        self.dataset_tables = None
        # Overview Tab
        self.overview_performance_metrics_selection_box = None
        self.overview_fairness_metrics_selection_box = None
        self.overview_modes_selection_box = None
        self.overview_sensitive_selection_box = None
        self.overview_table = None
        # Individual Tab
        self.individual_model_selection_box = None
        self.individual_metrics_selection_box = None
        self.individual_fairness_tables = None
        self.individual_performance_table = None

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

    def _populate_fairness_tabs(self, widget, pipeline, data_settings):
        widget.fairness.populate_fairness_tabs(pipeline, data_settings)

        # Dataset Tab
        self.dataset_tables = widget.fairness.sensitiveDatasetTable
        # Overview Tab
        self.overview_performance_metrics_selection_box = widget.fairness.cbPerformance
        self.overview_fairness_metrics_selection_box = widget.fairness.cbFairness
        self.overview_modes_selection_box = widget.fairness.cbOverviewModes
        self.overview_sensitive_selection_box = widget.fairness.cbSenstitiveAttributes
        self.overview_table = widget.fairness.overview_groupBox
        # Individual Tab
        self.individual_model_selection_box = widget.fairness.cbModels
        self.individual_metrics_selection_box = widget.fairness.individual_cbMetrics
        self.individual_performance_table = widget.fairness.individualPerformanceTable

        self.get_individual_fairness_tables = lambda: widget.fairness.sensitiveIndividualTables
