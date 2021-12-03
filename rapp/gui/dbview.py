import pandas as pd
from PyQt5 import QtCore
# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTableView
from PyQt5 import QtWidgets

from rapp import data
from rapp.gui.helper import Color


class PandasModel(QtCore.QAbstractTableModel):
    """
    TableModel to populate a PyQtTable with a Pandas DataFrame.
    Code from:
    https://github.com/eyllanesc/stackoverflow/blob/master/questions/44603119/PandasModel.py
    """

    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.iloc[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending=order ==
                                                QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class DataView(QtWidgets.QWidget):

    def __init__(self, parent=None, sql_conn=None):
        super(DataView, self).__init__(parent)

        self.combo = QtWidgets.QComboBox(self)
        self.combo.currentIndexChanged.connect(self.selection_changed)

        self.table = QtWidgets.QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.__sql_query = None
        self.__sql_idx = 0

        if sql_conn != None:
            self.set_connection(sql_conn)

    # TODO: Delete old database to insert new databaes?
    def set_connection(self, sql_connection):
        self.__conn = sql_connection

        cursor = self.__conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        self.combo.clear()
        for (tbl,) in cursor.fetchall():
            # we ignore some specifics here
            if tbl in ["migrate_version", "sqlite_sequence"]:
                continue
            self.combo.addItem(tbl)

        self.__sql_idx = self.combo.count()
        self.combo.addItem("SQL")
        self.combo.setCurrentIndex(0)

    def selection_changed(self, index):
        tbl = self.combo.itemText(index)
        print("Loading", tbl, "table")  ## Todo: proper logging

        if tbl != "SQL":
            sql_query = f'SELECT * FROM {tbl}'
            df = data.query_sql(sql_query, self.__conn)
            self.display_dataframe(df)
        elif self.__sql_query:
            df = data.query_sql(self.__sql_query, self.__conn)
            self.display_dataframe(df)
        else:
            self.display_dataframe(pd.DataFrame(columns=["Empty"]))

    def display_dataframe(self, df):
        """
        Display the given Pandas DataFrame in the widget.
        """
        model = PandasModel(df)
        self.table.setModel(model)

    def set_custom_sql(self, sql_query):
        df = data.query_sql(sql_query, self.__conn)
        model = PandasModel(df)
        self.table.setModel(model)
        self.__sql_query = sql_query
        self.combo.setCurrentIndex(self.__sql_idx)


class DatabaseLayoutWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(DatabaseLayoutWidget, self).__init__()
        self.initUI()

        self.filepath_db = "data/rapp.db"
        self.__conn = None  # Database connection.
        # self.connectDatabase(self.filepath_db)

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # create widgets
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        # self.pandasTv = DataView(self, self.__conn)
        self.pandasTv = Color('green', 'Database')
        sqlEditor = Color('blue', 'SQL Editor')
        actionbuttons = Color('yellow', 'Action buttons')

        # add widgets
        splitter.addWidget(self.pandasTv)
        splitter.addWidget(sqlEditor)

        # add to layout
        layout.addWidget(splitter)
        layout.addWidget(actionbuttons)

    def connectDatabase(self, filepath):
        print('Connecting to database')  # TODO: This should be a logging call.
        self.filepath_db = filepath
        self.__conn = data.connect(self.filepath_db)
        self.pandasTv.set_connection(self.__conn)
