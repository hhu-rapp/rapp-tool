# table
import pandas as pd
from pandas.io.sql import DatabaseError
import logging

# gui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# rapp
from rapp import gui
from rapp import data
from rapp.sqlbuilder import load_sql


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

    def __init__(self, parent=None, sql_conn=None, qmainwindow=None):
        super(DataView, self).__init__(parent)

        self.qmainwindow = qmainwindow

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
        logging.info(f'Loading {tbl} table')

        if self.qmainwindow is not None:
            msg = gui.helper.timeLogMsg('Loading ' + str(tbl) + ' table')
            self.qmainwindow.loggingTextBrowser.append(msg)
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
            msg = gui.helper.timeLogMsg(str(e))
            self.qmainwindow.loggingTextBrowser.append(msg)
            # print("Error in SQL code:", e)

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

        return df


class SimpleSQL(QtWidgets.QWidget):

    def __init__(self):
        super(SimpleSQL, self).__init__()

        self.initUI()
        self.template_sql = None

    def initUI(self):
        self.layout = QtWidgets.QFormLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Setup SQL templating
        self.featuresSelect = QtWidgets.QComboBox()
        self.featuresSelect.addItem("")
        self.featuresSelect.addItem("cs_first_term_modules")

        self.targetSelect = QtWidgets.QComboBox()
        self.targetSelect.addItem("")
        self.targetSelect.addItem("3_dropout")
        self.targetSelect.addItem("4term_ap")
        self.targetSelect.addItem("4term_cp")
        self.targetSelect.addItem("master_admission")
        self.targetSelect.addItem("rsz")

        self.verifySelect = QtWidgets.QPushButton("Load")
        self.verifySelect.clicked.connect(self.load_selected_sql_template)

        # add widgets to the layout
        self.layout.addRow('Features:', self.featuresSelect)
        self.layout.addRow('Target Variable:', self.targetSelect)
        self.layout.addRow(self.verifySelect)

    def load_selected_sql_template(self):
        logging.debug("Loading SQL template from GUI button click")

        f_id = self.featuresSelect.currentText()
        l_id = self.targetSelect.currentText()
        print(f"f_id = '{f_id}', l_id = '{l_id}'")

        if  f_id == "":
            logging.warning("No features chosen for SQL templating")
            return
        if l_id == "":
            logging.warning("No target label chosen for SQL templating")
            return

        sql = load_sql(f_id, l_id)

        self.template_sql = sql


class DatabaseLayoutWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow, filepath_db):
        super(DatabaseLayoutWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.filepath_db = filepath_db
        self.__conn = None
        self.sql_df = None

        self.initUI()
        self.connectDatabase(self.filepath_db) # init database

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.simpleSQL = SimpleSQL()

        # create widgets
        self.dbtab = QtWidgets.QTabWidget()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.pandasTv = DataView(self, sql_conn=self.__conn, qmainwindow=self.qmainwindow)
        self.sqlTbox = self.qmainwindow.sqlTbox

        # create buttons
        self.createButtons()

        # add tabs to TabWidget
        self.dbtab.addTab(self.simpleSQL, 'Simple')
        self.dbtab.addTab(self.sqlTbox, 'Advanced')

        # add widgets to splitter
        splitter.addWidget(self.pandasTv)
        # splitter.addWidget(self.sqlTbox)
        splitter.addWidget(self.dbtab)
        splitter.setSizes([400, 400])

        # add buttons to button layout
        self.hlayoutSqlButtons.addWidget(self.qPushButtonExecuteSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonUndoSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonRedoSql)
        self.hlayoutSqlButtons.addStretch(1)

        # add button actions
        self.qPushButtonExecuteSql.clicked.connect(lambda x: self.excute())
        self.qPushButtonUndoSql.clicked.connect(lambda x: self.sqlTbox.undo())
        self.qPushButtonRedoSql.clicked.connect(lambda x: self.sqlTbox.redo())

        # add to layout
        layout.addWidget(splitter)
        layout.addLayout(self.hlayoutSqlButtons)

    def excute(self):
        if self.dbtab.currentIndex() == 0: # simple
            pass
        elif self.dbtab.currentIndex() == 1: # advanced
            self.displaySql(self.sqlTbox.toPlainText())

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
        logging.info('Connecting to database')

        msg = gui.helper.timeLogMsg('Connecting to database')
        self.qmainwindow.loggingTextBrowser.append(msg)
        self.filepath_db = filepath
        self.__conn = data.connect(self.filepath_db)
        self.pandasTv.set_connection(self.__conn)

    def displaySql(self, sql_query=None):
        try:
            self.sql_df = self.pandasTv.set_custom_sql(sql_query)
            self.qmainwindow.sql_df = self.sql_df

            # TODO: better way to do access the method
            self.qmainwindow.tabs.MLTab.refresh_labels()

        except (DatabaseError, TypeError) as e:
            msg = gui.helper.timeLogMsg(str(e))

            self.qmainwindow.loggingTextBrowser.append(msg)
            # print("Error in SQL code:", e)
