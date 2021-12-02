# internal Python packages
import os
from datetime import datetime
import argparse

# rapp
from rapp.parser import RappConfigParser
from rapp.pipeline import MLPipeline

from rapp import data

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
# theme
from qt_material import apply_stylesheet

# dataframe
import pandas as pd
from pandas.io.sql import DatabaseError
from rapp.gui.dbview import DataView
from rapp.gui.menubar import MenuBar

# gui helper
from rapp.gui.helper import Color

db_filepath = "data/rapp.db"

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.__conn = None  # Database connection.

        self.initUI_deprecated()
        self.initLayout()
        # set menubar
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

        # set status bar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.connectDatabase(db_filepath)  # Hardcoded for now.

        # setup stylesheet
        # apply_stylesheet(self, theme='light_blue.xml')

    def initUI(self):
        # set the title
        self.setWindowTitle('Responsible Performance Prediction [Demoversion]')

        # setting the geometry of window
        self.width = 1280
        self.height = 720
        self.setGeometry(100, 60, self.width, self.height)

    def initLayout(self):
        pass

    def initUI_deprecated(self):
        # set the title
        self.setWindowTitle('Responsible Performance Prediction [Demoversion]')

        # setting the geometry of window
        self.width = 1280
        self.height = 720
        self.setGeometry(100, 60, self.width, self.height)

        # init tab and main widget
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        # create tabs
        self.dataExplorationTab = QtWidgets.QWidget()
        self.MLTab = QtWidgets.QWidget()
        self.XAITab = QtWidgets.QWidget()
        self.FairnessTab = QtWidgets.QWidget()

        # add tabs
        self.tabs.addTab(self.dataExplorationTab, 'Data Exploration')
        self.tabs.addTab(self.MLTab, 'Machine Learning')
        self.tabs.addTab(self.XAITab, 'Explainable AI')
        self.tabs.addTab(self.FairnessTab, 'Fairness')

        self.initDataExplorationTab()
        self.initMLTab()
        self.initXAITab()
        self.initFairnessTab()

    def initDataExplorationTab(self):
        self.vlayout = QtWidgets.QVBoxLayout()
        self.h1layout = QtWidgets.QHBoxLayout()
        self.v2layout = QtWidgets.QVBoxLayout()

        # vertical layout: main layout
        # self.vlayout.addWidget(Color('green', 'Menu Icons'), 1)

        # horizontal layout: pandas table and sql query
        self.pandasTv = DataView(self, self.__conn)
        self.h1layout.addWidget(self.pandasTv)

        # vertical layout: sql and data visualization
        # add menu buttons for SQL query
        self.hlayoutSqlButtons = QtWidgets.QHBoxLayout()
        self.qPushButtonExecuteSql = QtWidgets.QPushButton('Execute')
        self.hlayoutSqlButtons.addWidget(self.qPushButtonExecuteSql)
        self.qPushButtonUndoSql = QtWidgets.QPushButton('Undo')
        self.hlayoutSqlButtons.addWidget(self.qPushButtonUndoSql)
        self.qPushButtonRedoSql = QtWidgets.QPushButton('Redo')
        self.hlayoutSqlButtons.addWidget(self.qPushButtonRedoSql)
        self.v2layout.addLayout(self.hlayoutSqlButtons)

        # add SQL textbox
        self.sqlTbox = QtWidgets.QPlainTextEdit()
        self.v2layout.addWidget(self.sqlTbox)
        self.v2layout.addWidget(Color('yellow', 'plots, visuals with tabs'))

        # button actions
        self.qPushButtonExecuteSql.clicked.connect(lambda x: self.displaySql(self.sqlTbox.toPlainText()))
        self.qPushButtonUndoSql.clicked.connect(lambda x: self.sqlTbox.undo())
        self.qPushButtonRedoSql.clicked.connect(lambda x: self.sqlTbox.redo())

        # combining layouts
        self.h1layout.addLayout(self.v2layout)
        self.vlayout.addLayout(self.h1layout, 10)

        # add to tab layout
        self.dataExplorationTab.setLayout(self.vlayout)

    def initMLTab(self):
        self.vlayoutMainML = QtWidgets.QVBoxLayout()
        self.gridlayoutMainML = QtWidgets.QGridLayout()
        self.menubuttonsMainML = QtWidgets.QHBoxLayout()

        # self.vlayoutMainML.addWidget(Color('green', 'Menu Icons. Train. Validate. Stop.'))
        self.vlayoutMainML.addLayout(self.menubuttonsMainML)
        self.vlayoutMainML.addLayout(self.gridlayoutMainML)

        # menu buttons
        trainButton = QtWidgets.QPushButton('Train')
        validateButton = QtWidgets.QPushButton('Validate')
        self.menubuttonsMainML.addWidget(trainButton)
        trainButton.clicked.connect(self.train)
        self.menubuttonsMainML.addWidget(validateButton)
        validateButton.clicked.connect(self.validate)

        # labels
        self.labelName = QtWidgets.QLabel()
        self.labelName.setText('Target Variable:')

        self.labelCVariables = QtWidgets.QLabel()
        self.labelCVariables.setText('Categorical Variables:')

        self.labelType = QtWidgets.QLabel()
        self.labelType.setText('Type:')

        self.labelReportPath = QtWidgets.QLabel()
        self.labelReportPath.setText('Report Path:')

        self.labelImputation = QtWidgets.QLabel()
        self.labelImputation.setText('Imputation Method:')

        self.labelFSM = QtWidgets.QLabel()
        self.labelFSM.setText('Feature Selection Method:')

        # create menus for configuration
        self.leName = QtWidgets.QLineEdit()
        self.leCVariables = QtWidgets.QLineEdit()
        self.cbType = QtWidgets.QComboBox()
        self.cbType.addItem('Classification')
        self.cbType.addItem('Regression')
        self.lePath = QtWidgets.QLineEdit()
        self.cbImputation = QtWidgets.QComboBox()
        self.cbImputation.addItem('Iterative')
        self.cbFSM = QtWidgets.QComboBox()
        self.cbFSM.addItem('Variance')

        # add labels to the grid
        self.gridlayoutMainML.addWidget(self.labelName, 0, 0)
        self.gridlayoutMainML.addWidget(self.labelCVariables, 1, 0)
        self.gridlayoutMainML.addWidget(self.labelType, 2, 0)
        self.gridlayoutMainML.addWidget(self.labelReportPath, 3, 0)
        self.gridlayoutMainML.addWidget(self.labelImputation, 4, 0)
        self.gridlayoutMainML.addWidget(self.labelFSM, 5, 0)

        # add options to the grid
        self.gridlayoutMainML.addWidget(self.leName, 0, 1)
        self.gridlayoutMainML.addWidget(self.leCVariables, 1, 1)
        self.gridlayoutMainML.addWidget(self.cbType, 2, 1)
        self.gridlayoutMainML.addWidget(self.lePath, 3, 1)
        self.gridlayoutMainML.addWidget(self.cbImputation, 4, 1)
        self.gridlayoutMainML.addWidget(self.cbFSM, 5, 1)

        # add to tab layout
        self.MLTab.setLayout(self.vlayoutMainML)

    def initXAITab(self):
        pass

    def initFairnessTab(self):
        pass

    def train(self):
        """
        Get user input and parse to MLPipeline
        Returns
        -------

        """
        # temporarily save currenty sql query
        sqlQueryTempPath = os.getcwd() + 'sqlTemp' + datetime.now().time().strftime("%b-%d-%Y") + '.sql'
        print(sqlQueryTempPath)
        with open(sqlQueryTempPath, "w") as text_file:
            text_file.write(self.sqlTbox.toPlainText())

        args = argparse.Namespace()
        args.filename = db_filepath
        args.sql_filename = sqlQueryTempPath
        args.label_name = self.leName.text()
        args.categorical = self.leCVariables.text().replace(' ', '').split(',')
        args.type = self.cbType.currentText().lower()
        args.imputation = self.cbImputation.currentText().lower()
        args.feature_selection = self.cbFSM.currentText().lower()
        args.plot_confusion_matrix = 'True'
        args.report_path = ''
        args.save_report = 'True'
        args.sensitive_attributes = []
        args.classifier = None

        MLPipeline(args)

        # remove temporary files
        os.remove(sqlQueryTempPath)

    def validate(self):
        pass

    def connectDatabase(self, filepath):
        print('Connecting to database')  # TODO: This should be a logging call.
        self.filepath_db = filepath
        self.__conn = data.connect(self.filepath_db)
        self.pandasTv.set_connection(self.__conn)

    def displaySql(self, sql_query=None):
        try:
            self.pandasTv.set_custom_sql(sql_query)
        except (DatabaseError, TypeError) as e:
            self.statusbar.setStatusTip(str(e))
            print("Error in SQL code:", e)
