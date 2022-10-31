# table
import pandas as pd
from pandas.io.sql import DatabaseError
import logging
log = logging.getLogger('GUI')

# gui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# rapp
from rapp import gui
from rapp import data
from rapp.gui.sql import SQLWidget
from rapp.sqlbuilder import load_sql


class PandasModel(QtCore.QAbstractTableModel):
    """
    TableModel to populate a PyQtTable with a Pandas DataFrame.
    Code from:
    https://github.com/eyllanesc/stackoverflow/blob/master/questions/44603119/PandasModel.py
    """

    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self.df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self.df.columns.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self.df.index.tolist()[section]
            except (IndexError,):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self.df.iloc[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self.df.index[index.row()]
        col = self.df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self.df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self.df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.df.columns)

    def sort(self, column, order):
        colname = self.df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self.df.sort_values(colname, ascending=order ==
                                               QtCore.Qt.AscendingOrder, inplace=True)
        self.df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class DataView(QtWidgets.QWidget):

    def __init__(self, parent=None, sql_conn=None, qmainwindow=None):
        super(DataView, self).__init__(parent)

        self.qmainwindow = qmainwindow

        self.combo = QtWidgets.QComboBox(self)
        self.combo.currentIndexChanged.connect(self.selection_changed)

        self.table = QtWidgets.QTableView(self)
        self.table.setSortingEnabled(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.table)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.__sql_query = None
        self.__sql_idx = 0

        if sql_conn != None:
            self.set_connection(sql_conn)

    def set_connection(self, sql_connection):
        # TODO Bug: Delete old database to insert new database
        self.__conn = sql_connection
        self.__sql_query = None

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
        log.info(f'Loading {tbl} table')

        try:
            if tbl != "SQL" and tbl != "":
                sql_query = f'SELECT * FROM {tbl}'
                df = data.query_sql(sql_query, self.__conn)
                self.display_dataframe(df)
            elif self.__sql_query:
                df = data.query_sql(self.__sql_query, self.__conn)
                self.display_dataframe(df)
            else:
                self.display_dataframe(pd.DataFrame(columns=["Empty"]))

        except (DatabaseError, TypeError) as e:
            log.error(str(e))

    def display_dataframe(self, df):
        """
        Display the given Pandas DataFrame in the widget.
        """
        model = PandasModel(df)
        self.table.setModel(model)

    def set_custom_sql(self, sql_query):
        df = data.query_sql(sql_query, self.__conn)
        df.columns = df.columns.str.capitalize()
        model = PandasModel(df)
        self.table.setModel(model)
        self.__sql_query = sql_query
        self.combo.setCurrentIndex(self.__sql_idx)

        return df

    def get_custom_sql(self):
        return self.__sql_query


class DatabaseLayoutWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow, filepath_db):
        super(DatabaseLayoutWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.filepath_db = filepath_db
        self.__conn = None
        self.sql_df = None
        self.features_id = None
        self.labels_id = None

        self.initUI()
        self.connectDatabase(self.filepath_db) # init database

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # create widgets
        self.sql_tabs = SQLWidget(sql_query_callback=self.displaySql)
        self.pandas_dataview = DataView(self, sql_conn=self.__conn, qmainwindow=self.qmainwindow)

        # add widgets to splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.pandas_dataview)
        splitter.addWidget(self.sql_tabs)
        splitter.setSizes([400, 400])

        # add to layout
        layout.addWidget(splitter)

    def createButtons(self):
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

    def connectDatabase(self, filepath):
        log.info('Connecting to database %s', filepath)

        self.filepath_db = filepath
        self.sql_tabs.set_db_filepath(filepath)
        self.__conn = data.connect(self.filepath_db)
        self.pandas_dataview.set_connection(self.__conn)

    def displaySql(self, sql_query=None, f_id=None, l_id=None):

        try:
            self.sql_df = self.pandas_dataview.set_custom_sql(sql_query)

            self.features_id = f_id
            self.labels_id = l_id

            self.qmainwindow.sql_df = self.sql_df

            # TODO: better way to do access the method
            self.qmainwindow.settings.simple_tab.refresh_labels()
            self.qmainwindow.prediction.refresh_labels()

        except (DatabaseError, TypeError) as e:
            log.error(str(e))

    def get_current_df(self):
        return self.pandas_dataview.table.model().df

    def get_current_template_id(self):
        return self.features_id, self.labels_id

    def getDataSettings(self):
        # TODO: Cannot access current dataframe
        current_df = self.pandas_dataview.table.model().df
        return current_df, self.features_id, self.labels_id

    def load_sql(self, sql_query):
        self.sql_tabs.set_sql(sql_query)
