# internal Python packages
import sys
import sqlite3

# PyQt5
import PyQt5.QtCore
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

# dataframe
import pandas as pd
from pdmodel import PandasModel


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

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

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
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
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

        self.initUI()
        # self.initMenu()
        #self.retranslateUi()
        #self.initMenuAction()

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
        self.vlayout.addWidget(Color('red', 'Menubar'), 0)
        self.vlayout.addWidget(Color('green', 'Menu Icons'), 1)

        # horizontal layout: pandas table and sql query
        self.h1layout.addWidget(Color('blue', 'Dataframe'))

        # vertical layout: sql and data visualization
        self.v2layout.addWidget(Color('brown', 'SQL query textfield'))
        self.v2layout.addWidget(Color('yellow', 'plots, visuals with tabs'))

        # combining layouts
        self.h1layout.addLayout(self.v2layout)
        self.vlayout.addLayout(self.h1layout, 10)

        #self.setLayout(self.vlayout)
        wid.setLayout(self.vlayout)

    def initMenu(self):
        #self.vLayout = QtWidgets.QVBoxLayout(self)
        #self.hLayout = QtWidgets.QHBoxLayout()

        # Menubar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, self.width, 24))
        self.menubar.setObjectName("menubar")

        # Menu
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")

        self.setMenuBar(self.menubar)

        # status bar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # setting actions for the menu
        # File
        self.actionOpen_Database = QtWidgets.QAction(self)
        self.actionOpen_Database.setObjectName("actionOpen_Database")
        self.actionOpen_SQLite_Query = QtWidgets.QAction(self)
        self.actionOpen_SQLite_Query.setObjectName("actionOpen_SQLite_Query")

        # Edit
        self.actionCopy = QtWidgets.QAction(self)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(self)
        self.actionPaste.setObjectName("actionPaste")

        # add entries to the menu
        self.menuFile.addAction(self.actionOpen_Database)
        self.menuFile.addAction(self.actionOpen_SQLite_Query)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)

        # adding to menubar
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        # Table view
        self.pandasTv = QtWidgets.QTableView(self)
        self.pandasTv.move(0, 24)

        # arrange layout
        #self.vLayout.addWidget(self.menubar)
        #self.vLayout.addWidget(self.pandasTv)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Window", "MainWindow"))
        self.menuFile.setTitle(_translate("Window", "File"))
        self.menuEdit.setTitle(_translate("Window", "Edit"))

        self.actionOpen_Database.setText(_translate("Window", "Open Database"))
        self.actionOpen_Database.setStatusTip(_translate("Window", "Opens SQLite Database. File type is \'.db\'"))
        self.actionOpen_Database.setShortcut(_translate("Window", "Ctrl+O"))

        self.actionOpen_SQLite_Query.setText(_translate("Window", "Open SQLite Query"))
        self.actionOpen_SQLite_Query.setStatusTip(_translate("Window", "Opens an SQLite query file"))

        self.actionCopy.setText(_translate("Window", "Copy"))
        self.actionPaste.setText(_translate("Window", "Paste"))

    def initMenuAction(self):
        self.actionOpen_Database.triggered.connect(self.openDatabase)

    def openDatabase(self):
        print('Opening Database')
        self.filepath_db = QtWidgets.QFileDialog.getOpenFileName()[0]
        con = sqlite3.connect(self.filepath_db)
        df = pd.read_sql_query('SELECT * FROM Einschreibung', con)
        #df = pd.read_sql(con)
        # df = pd.read_csv(self.filepath_db)
        model = PandasModel(df)
        self.pandasTv.setModel(model)
        self.pandasTv.resizeColumnsToContents()


if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # start the app
    sys.exit(App.exec())
