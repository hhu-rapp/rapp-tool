# internal Python packages
import sqlite3

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

        # init layout
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
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
        self.hlayout_sqlButtons = QtWidgets.QHBoxLayout()
        self.hlayout_sqlButtons.addWidget(QtWidgets.QPushButton('Execute'))
        self.hlayout_sqlButtons.addWidget(QtWidgets.QPushButton('Undo'))
        self.hlayout_sqlButtons.addWidget(QtWidgets.QPushButton('Redo'))
        self.v2layout.addLayout(self.hlayout_sqlButtons)

        # add SQL textbox
        self.sqlTbox = QtWidgets.QPlainTextEdit()
        self.v2layout.addWidget(self.sqlTbox)
        self.v2layout.addWidget(Color('yellow', 'plots, visuals with tabs'))

        # combining layouts
        self.h1layout.addLayout(self.v2layout)
        self.vlayout.addLayout(self.h1layout, 10)

        # self.setLayout(self.vlayout)
        wid.setLayout(self.vlayout)

    def connectDatabase(self, filepath):
        print('Connecting to database')  # TODO: This should be a logging call.
        self.filepath_db = filepath
        self.__conn = sqlite3.connect(self.filepath_db)
        self.pandasTv.set_connection(self.__conn)

    def displayData(self, sql_query):
        df = pd.read_sql_query(sql_query, self.__conn)
        self.pandasTv.display_dataframe(df)
