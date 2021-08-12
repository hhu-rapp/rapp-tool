import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableView


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
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
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


class DataView(QWidget):

    def __init__(self, parent=None, sql_conn=None):
        super(DataView, self).__init__(parent)

        self.combo = QComboBox(self)
        self.combo.currentIndexChanged.connect(self.selection_changed)

        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.resizeColumnsToContents()

        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.table)
        self.setLayout(layout)

        if sql_conn != None:
            self.set_connection(sql_conn)


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

        if self.combo.count() > 0:
            self.combo.itemText(0)

    def selection_changed(self, index):
        tbl = self.combo.itemText(index)
        print("Loading", tbl, "table")  ## Todo: proper logging

        sql_query = f'SELECT * FROM {tbl}'
        df = pd.read_sql_query(sql_query, self.__conn)
        self.display_dataframe(df)

    def display_dataframe(self, df):
        """
        Display the given Pandas DataFrame in the widget.
        """
        model = PandasModel(df)
        self.table.setModel(model)
