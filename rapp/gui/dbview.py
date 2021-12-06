# table
import pandas as pd
from pandas.io.sql import DatabaseError

# gui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# rapp
from rapp import gui
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
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.__sql_query = None
        self.__sql_idx = 0

        if sql_conn != None:
            self.set_connection(sql_conn)

    # TODO Bug: Delete old database to insert new database
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

    def __init__(self, filepath_db):
        super(DatabaseLayoutWidget, self).__init__()

        self.filepath_db = filepath_db
        self.__conn = None  # Database connection.

        self.initUI()
        self.connectDatabase(self.filepath_db) # init database

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # create widgets
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.pandasTv = DataView(self, self.__conn)
        self.sqlTbox = QtWidgets.QPlainTextEdit()

        # create buttons
        self.hlayoutSqlButtons = QtWidgets.QHBoxLayout()
        self.hlayoutSqlButtons.setContentsMargins(0, 0, 0, 0)

        self.qPushButtonExecuteSql = QtWidgets.QPushButton()
        self.qPushButtonExecuteSql.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_MediaPlay')))
        self.qPushButtonExecuteSql.setStatusTip('Execute SQL query (Ctrl+Enter)')
        self.qPushButtonExecuteSql.setShortcut('Ctrl+Return')

        self.qPushButtonUndoSql = QtWidgets.QPushButton()
        self.qPushButtonUndoSql.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ArrowBack')))
        self.qPushButtonUndoSql.setStatusTip('Undo text (Ctrl+Z)')
        self.qPushButtonUndoSql.setShortcut('Ctrl+Z')

        self.qPushButtonRedoSql = QtWidgets.QPushButton()
        self.qPushButtonRedoSql.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ArrowForward')))
        self.qPushButtonRedoSql.setStatusTip('Redo text (Ctrl+Shift+Z)')
        self.qPushButtonRedoSql.setShortcut('Ctrl+Shift+Z')

        # add widgets to splitter
        splitter.addWidget(self.pandasTv)
        splitter.addWidget(self.sqlTbox)
        splitter.setSizes([400, 400])

        # add buttons to button layout
        self.hlayoutSqlButtons.addWidget(self.qPushButtonExecuteSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonUndoSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonRedoSql)
        self.hlayoutSqlButtons.addStretch(1)

        # add button actions
        self.qPushButtonExecuteSql.clicked.connect(lambda x: self.displaySql(self.sqlTbox.toPlainText()))
        self.qPushButtonUndoSql.clicked.connect(lambda x: self.sqlTbox.undo())
        self.qPushButtonRedoSql.clicked.connect(lambda x: self.sqlTbox.redo())

        # add to layout
        layout.addWidget(splitter)
        layout.addLayout(self.hlayoutSqlButtons)

    def connectDatabase(self, filepath):
        print('Connecting to database')  # TODO: This should be a logging call.
        self.filepath_db = filepath
        self.__conn = data.connect(self.filepath_db)
        self.pandasTv.set_connection(self.__conn)

    def displaySql(self, sql_query=None):
        try:
            self.pandasTv.set_custom_sql(sql_query)

            # save temporary sql file
            with open(gui.sql_temp_path, "w") as text_file:
                text_file.write(self.sqlTbox.toPlainText())

        except (DatabaseError, TypeError) as e:
            self.statusbar.setStatusTip(str(e))
            print("Error in SQL code:", e)
