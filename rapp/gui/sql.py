import logging

import pandas as pd
from pandas.io.sql import DatabaseError

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from rapp.sqlbuilder import load_sql


class SQLWidget(QtWidgets.QWidget):

    def __init__(self, sql_query_callback):
        """
        Parameters
        ----------
        sql_query_callback: function
            A reference to a function that takes an SQL query as argument.
        """
        super(SQLWidget, self).__init__()

        self.displaySql = sql_query_callback

        self.tabs = QtWidgets.QTabWidget()
        self.__init_simple_tab()
        self.__init_advanced_tab()

        self.__is_reset_connected = False

        # Arrange layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def __init_simple_tab(self):
        self.simple_tab = QtWidgets.QWidget()
        self.simple_tab.setLayout(QtWidgets.QFormLayout())

        # Setup SQL templating
        self.featuresSelect = QtWidgets.QComboBox()
        self.featuresSelect.addItem("")
        self.featuresSelect.addItem("cs_first_term_modules")
        self.featuresSelect.addItem("cs_first_term_grades")
        self.featuresSelect.addItem("cs_first_term_ects")

        self.targetSelect = QtWidgets.QComboBox()
        self.targetSelect.addItem("")
        self.targetSelect.addItem("3_dropout")
        self.targetSelect.addItem("4term_ap")
        self.targetSelect.addItem("4term_cp")
        self.targetSelect.addItem("master_admission")
        self.targetSelect.addItem("rsz")

        self.verifySelect = QtWidgets.QPushButton("Load")
        self.verifySelect.clicked.connect(self.load_selected_sql_template)

        # add to layout
        self.simple_tab.layout().addRow('Features:', self.featuresSelect)
        self.simple_tab.layout().addRow('Target Variable:', self.targetSelect)
        self.simple_tab.layout().addRow(self.verifySelect)

        self.tabs.addTab(self.simple_tab, 'Simple')

    def __init_advanced_tab(self):
        self.sql_field = QtWidgets.QPlainTextEdit()
        self.sql_field.setPlaceholderText("Enter custom SQL query here.")

        self.advanced_tab = QtWidgets.QWidget()
        self.advanced_tab.setLayout(QtWidgets.QVBoxLayout())

        self.__init_buttons()
        self.advanced_tab.layout().addWidget(self.sql_field)
        self.advanced_tab.layout().addLayout(self.hlayoutSqlButtons)

        tab_idx = self.tabs.addTab(self.advanced_tab, 'Advanced')
        self.__advanced_tab_index = tab_idx

    def __init_buttons(self):
        self.hlayoutSqlButtons = QtWidgets.QHBoxLayout()
        self.hlayoutSqlButtons.setContentsMargins(0, 0, 0, 0)

        self.qPushButtonExecuteSql = QtWidgets.QPushButton()
        self.qPushButtonExecuteSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_MediaPlay')))
        self.qPushButtonExecuteSql.setStatusTip(
            'Execute SQL query (Ctrl+Enter)')
        self.qPushButtonExecuteSql.setShortcut('Ctrl+Return')

        self.qPushButtonUndoSql = QtWidgets.QPushButton()
        self.qPushButtonUndoSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_ArrowBack')))
        self.qPushButtonUndoSql.setStatusTip('Undo text (Ctrl+Z)')
        self.qPushButtonUndoSql.setShortcut('Ctrl+Z')

        self.qPushButtonRedoSql = QtWidgets.QPushButton()
        self.qPushButtonRedoSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_ArrowForward')))
        self.qPushButtonRedoSql.setStatusTip('Redo text (Ctrl+Shift+Z)')
        self.qPushButtonRedoSql.setShortcut('Ctrl+Shift+Z')

        # add buttons to button layout
        self.hlayoutSqlButtons.addWidget(self.qPushButtonExecuteSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonUndoSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonRedoSql)
        self.hlayoutSqlButtons.addStretch(1)

        # add button actions
        self.qPushButtonExecuteSql.clicked.connect(
            lambda: self.displaySql(self.sql_field.toPlainText())
        )
        self.qPushButtonUndoSql.clicked.connect(self.sql_field.undo)
        self.qPushButtonRedoSql.clicked.connect(self.sql_field.redo)

    def load_selected_sql_template(self):
        logging.debug("Loading SQL template from GUI button click")

        f_id = self.featuresSelect.currentText()
        l_id = self.targetSelect.currentText()
        print(f"f_id = '{f_id}', l_id = '{l_id}'")

        if f_id == "":
            logging.warning("No features chosen for SQL templating")
            return
        if l_id == "":
            logging.warning("No target label chosen for SQL templating")
            return

        # Display the queried template in the advanced tab
        sql = load_sql(f_id, l_id)
        self.sql_field.setPlainText(sql)

        # Load the data
        self.displaySql(sql)

        # Changing the custom SQL should reset the selections.
        self.sql_field.textChanged.connect(self.reset_simple_tab)
        self.__is_reset_connected = True

    def reset_simple_tab(self):
        logging.debug("Resetting selection in Simple SQL tab")
        self.featuresSelect.setCurrentIndex(0)
        self.targetSelect.setCurrentIndex(0)

        # Once reset, the connection between the custom SQL field and
        # the simple selectors is no longer given
        if self.__is_reset_connected:
            self.sql_field.textChanged.disconnect(self.reset_simple_tab)
            self.__is_reset_connected = False

    def set_sql(self, sql_query):
        """
        Loads the given query into the SQL text field.
        """
        logging.debug("Setting SQL query by external call")
        self.reset_simple_tab()
        self.sql_field.setPlainText(sql_query)

        # Change to advanced tab.
        self.tabs.setCurrentIndex(self.__advanced_tab_index)
