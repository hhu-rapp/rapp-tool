# internal Python packages
import os
from datetime import datetime
import sqlite3
import argparse

# rapp
from rapp.parser import parse_rapp_args
from rapp import MLPipeline

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow

# dataframe
import pandas as pd
from rapp.gui.dbview import DataView
from rapp.gui.menubar import MenuBar


class DataFrameModel(QtCore.QAbstractTableModel):
    """
    From stackoverflow:
    https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5-pyside2
    """
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(
        pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()
                                       and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class Color(QtWidgets.QWidget):
    # Works as a placeholder
    def __init__(self, color, label_str='Label'):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        # background color
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))

        # label
        label = QtWidgets.QLabel()
        label.setText(label_str)
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0)

        self.setLayout(layout)
        self.setPalette(palette)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.__conn = None  # Database connection.

        self.initUI()
        # set menubar
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)

        # set status bar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.connectDatabase("data/rapp.db")  # Hardcoded for now.

        self.show()

    def initUI(self):
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
        # TODO: scope? global variables via self or local?

        self.vlayout = QtWidgets.QVBoxLayout()
        self.h1layout = QtWidgets.QHBoxLayout()
        self.v2layout = QtWidgets.QVBoxLayout()

        # vertical layout: main layout
        self.vlayout.addWidget(Color('green', 'Menu Icons'), 1)

        # horizontal layout: pandas table and sql query
        self.pandasTv = DataView(self, self.__conn)
        self.h1layout.addWidget(self.pandasTv)

        # vertical layout: sql and data visualization
        # add menu buttons for SQL query
        self.hlayoutSqlButtons = QtWidgets.QHBoxLayout()
        self.qPushButtonExcuteSql = QtWidgets.QPushButton('Execute')
        self.hlayoutSqlButtons.addWidget(self.qPushButtonExcuteSql)
        self.hlayoutSqlButtons.addWidget(QtWidgets.QPushButton('Undo'))
        self.hlayoutSqlButtons.addWidget(QtWidgets.QPushButton('Redo'))
        self.v2layout.addLayout(self.hlayoutSqlButtons)

        # add SQL textbox
        self.sqlTbox = QtWidgets.QPlainTextEdit()
        self.v2layout.addWidget(self.sqlTbox)
        self.v2layout.addWidget(Color('yellow', 'plots, visuals with tabs'))

        try:
            self.qPushButtonExcuteSql.clicked.connect(lambda x: self.displayData(self.sqlTbox.toPlainText()))
        except Exception as e:
            # TODO: Why doesnt it work? Faulty sql queries will crash the program
            self.statusbar.setStatusTip(str(e))

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
        parser = argparse.ArgumentParser()
        parser = parse_rapp_args(parser)

        # temporarily save currenty sql query
        sqlQueryTempPath = os.getcwd()+'sqlTemp'+datetime.now().time().strftime("%b-%d-%Y")+'.sql'
        print(sqlQueryTempPath)
        with open(sqlQueryTempPath, "w") as text_file:
            text_file.write(self.sqlTbox.toPlainText())

        args = argparse.Namespace()
        args.filename = 'data/rapp.db'
        args.sql_filename = sqlQueryTempPath
        args.label_name = self.leName.text()
        args.categorical = self.leCVariables.text().replace(' ', '').split(',')
        args.type = self.cbType.currentText().lower()
        args.imputation = self.cbImputation.currentText().lower()
        args.feature_selection = self.cbFSM.currentText().lower()
        args.plot_confusion_matrix = 'True'
        args.report_path = ''
        args.save_report = 'True'

        # try:
        MLPipeline(args)

        # remove temporary files
        os.remove(sqlQueryTempPath)

    def validate(self):
        pass

    def connectDatabase(self, filepath):
        print('Connecting to database')  # TODO: This should be a logging call.
        self.filepath_db = filepath
        self.__conn = sqlite3.connect(self.filepath_db)
        self.pandasTv.set_connection(self.__conn)

    def displayData(self, sql_query):
        df = pd.read_sql_query(sql_query, self.__conn)
        self.pandasTv.display_dataframe(df)
