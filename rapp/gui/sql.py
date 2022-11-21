import pathlib
from os.path import basename

from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets

from rapp.gui.helper import Highlighter, init_sql_highlighter
from rapp.sqlbuilder import load_sql
from rapp import sqlbuilder


class SQLWidget(QtWidgets.QWidget):

    def __init__(self, sql_query_callback, log):
        """
        Parameters
        ----------
        sql_query_callback: function
            A reference to a function that takes an SQL query as argument.

        log: logger instance
        """
        super(SQLWidget, self).__init__()
        self.log = log

        self.displaySql = sql_query_callback

        self.db_filepath = None

        self.tabs = QtWidgets.QTabWidget()
        self.__init_simple_tab()
        self.__init_advanced_tab()

        self.__is_reset_connected = False

        self.setAcceptDrops(True)

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
        self.targetSelect = QtWidgets.QComboBox()
        self.__populate_template_options()

        self.verifySelect = QtWidgets.QPushButton("Load Templates")
        self.verifySelect.clicked.connect(self.load_selected_sql_template)

        # add to layout
        self.simple_tab.layout().addRow('Features:', self.featuresSelect)
        self.simple_tab.layout().addRow('Target Variable:', self.targetSelect)
        self.simple_tab.layout().addRow(self.verifySelect)

        self.tabs.addTab(self.simple_tab, 'Templates')

    def __populate_template_options(self):
        """
        Populates the template options in the simple tab.
        """
        self.featuresSelect.clear()
        self.targetSelect.clear()
        # setup path
        dirs_feats = sqlbuilder.list_available_features()
        dirs_labels = sqlbuilder.list_available_labels()

        self.featuresSelect.addItem("")
        for feat_id in dirs_feats:
            self.log.debug(f"Adding feature '{feat_id}' to SQL templates")
            self.featuresSelect.addItem(feat_id)

        self.targetSelect.addItem("")
        for label_id in dirs_labels:
            self.log.debug(f"Adding label '{label_id}' to SQL templates")
            self.targetSelect.addItem(label_id)

    def __init_advanced_tab(self):
        self.sql_field = QtWidgets.QPlainTextEdit()
        self.sql_field.setPlaceholderText("Enter custom SQL query here.")

        self.advanced_tab = QtWidgets.QWidget()
        self.advanced_tab.setLayout(QtWidgets.QVBoxLayout())

        self.highlighter = Highlighter()
        self.Findhighlighter = Highlighter()
        init_sql_highlighter(self.highlighter, self.sql_field)

        self.__init_buttons()
        self.advanced_tab.layout().addLayout(self.hlayoutSqlButtons)
        self.advanced_tab.layout().addWidget(self.sql_field)

        tab_idx = self.tabs.addTab(self.advanced_tab, 'SQL Query')
        self.advanced_tab_index = tab_idx

    def __init_buttons(self):
        self.hlayoutSqlButtons = QtWidgets.QHBoxLayout()
        self.hlayoutSqlButtons.setContentsMargins(0, 0, 0, 0)

        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.VLine)
        separator1.setFrameShadow(QtWidgets.QFrame.Sunken)

        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.VLine)
        separator2.setFrameShadow(QtWidgets.QFrame.Sunken)

        separator3 = QtWidgets.QFrame()
        separator3.setFrameShape(QtWidgets.QFrame.VLine)
        separator3.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.qPushButtonOpenSql = QtWidgets.QPushButton()
        self.qPushButtonOpenSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DirOpenIcon')))
        self.qPushButtonOpenSql.setStatusTip(
            'Open SQL query (Ctrl+Shift+O)')
        self.qPushButtonOpenSql.setShortcut('Ctrl+Shift+O')

        self.qPushButtonSaveSql = QtWidgets.QPushButton()
        self.qPushButtonSaveSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DialogSaveButton')))
        self.qPushButtonSaveSql.setStatusTip('Save current SQL query (Ctrl+Shift+S)')
        self.qPushButtonSaveSql.setShortcut('Ctrl+Shift+S')

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

        self.qPushButtonClearSql = QtWidgets.QPushButton()
        self.qPushButtonClearSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DialogResetButton')))
        self.qPushButtonClearSql.setStatusTip('Clear SQL query (Ctrl+Shift+Delete)')
        self.qPushButtonClearSql.setShortcut('Ctrl+Shift+Delete')

        self.qPushButtonInsertSql = QtWidgets.QPushButton("+")
        self.qPushButtonInsertSql.setFixedSize(32, 28)
        self.qPushButtonInsertSql.setStatusTip('Insert into table (Ctrl+N)')
        self.qPushButtonInsertSql.setShortcut('Ctrl+N')

        self.qLineEditFindSql = QtWidgets.QLineEdit()
        self.qLineEditFindSql.setHidden(True)
        self.qLineEditFindSql.setPlaceholderText("Find keyword")

        self.qLabelFoundResults = QtWidgets.QLabel()
        self.qLabelFoundResults.setHidden(True)

        self.qPushButtonFindPrevious = QtWidgets.QPushButton()
        self.qPushButtonFindPrevious.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_TitleBarShadeButton')))
        self.qPushButtonFindPrevious.setStatusTip('Find Previous (Shift+F3)')
        self.qPushButtonFindPrevious.setShortcut('Shift+F3')
        self.qPushButtonFindPrevious.setHidden(True)

        self.qPushButtonFindNext = QtWidgets.QPushButton()
        self.qPushButtonFindNext.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_TitleBarUnshadeButton')))
        self.qPushButtonFindNext.setStatusTip('Find Next (F3)')
        self.qPushButtonFindNext.setShortcut('F3')
        self.qPushButtonFindNext.setHidden(True)

        self.qPushButtonFindSql = QtWidgets.QPushButton()
        self.qPushButtonFindSql.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_FileDialogContentsView')))
        self.qPushButtonFindSql.setStatusTip('Find in SQL Query (Ctrl+F)')
        self.qPushButtonFindSql.setShortcut('Ctrl+F')

        # add buttons to button layout
        self.hlayoutSqlButtons.addWidget(self.qPushButtonOpenSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonSaveSql)
        self.hlayoutSqlButtons.addWidget(separator1)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonExecuteSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonUndoSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonRedoSql)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonClearSql)
        self.hlayoutSqlButtons.addWidget(separator2)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonInsertSql)
        self.hlayoutSqlButtons.addWidget(separator3)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonFindSql)
        self.hlayoutSqlButtons.addWidget(self.qLineEditFindSql)
        self.hlayoutSqlButtons.addWidget(self.qLabelFoundResults)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonFindPrevious)
        self.hlayoutSqlButtons.addWidget(self.qPushButtonFindNext)
        self.hlayoutSqlButtons.addStretch(1)

        # add button actions
        self.qPushButtonOpenSql.clicked.connect(self.open_sql_query)
        self.qPushButtonSaveSql.clicked.connect(self.save_sql_query)
        self.qPushButtonExecuteSql.clicked.connect(
            lambda: self.displaySql(self.sql_field.toPlainText())
        )
        self.qPushButtonClearSql.clicked.connect(
            lambda: self.sql_field.setPlainText(''))
        self.qPushButtonUndoSql.clicked.connect(self.sql_field.undo)
        self.qPushButtonRedoSql.clicked.connect(self.sql_field.redo)
        self.qPushButtonInsertSql.clicked.connect(self.insert_sql)
        self.qPushButtonFindSql.clicked.connect(self.toggle_find_sql)

    def load_selected_sql_template(self):
        self.log.debug("Loading SQL template from GUI button click")

        f_id = self.featuresSelect.currentText()
        l_id = self.targetSelect.currentText()
        self.log.debug(f"f_id = '{f_id}', l_id = '{l_id}'")

        if f_id == "":
            self.log.warning("No features chosen for SQL templating")
            return
        if l_id == "":
            self.log.warning("No target label chosen for SQL templating")
            return

        # Display the queried template in the advanced tab
        sql = load_sql(f_id, l_id)
        self.sql_field.setPlainText(sql)

        # Load the data
        self.displaySql(sql, f_id, l_id)

        # Changing the custom SQL should reset the selections.
        self.sql_field.textChanged.connect(self.reset_simple_tab)
        self.__is_reset_connected = True

    def set_template_ids(self, f_id=None, l_id=None):
        if f_id is not None:
            self.featuresSelect.setCurrentText(f_id)
        if l_id is not None:
            self.targetSelect.setCurrentText(l_id)

        self.load_selected_sql_template()

    def reset_simple_tab(self):
        self.log.debug("Resetting selection in Simple SQL tab")
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
        self.log.debug("Setting SQL query by external call")
        self.reset_simple_tab()
        self.sql_field.setPlainText(sql_query)

        # Change to advanced tab.
        self.tabs.setCurrentIndex(self.advanced_tab_index)

    def set_db_filepath(self, path):
        """
        Sets the database filepath to the given path.
        """
        self.log.debug("Setting database filepath by external call to %s", path)
        self.db_filepath = path

        sqlbuilder.set_database_name(basename(self.db_filepath))
        self.__populate_template_options()

    def toggle_find_sql(self):
        """
        Toggles SQL search bar.
        """

        if self.qLineEditFindSql.isHidden():
            # show line edit
            self.qLineEditFindSql.setHidden(False)
            self.qLineEditFindSql.setFocus()

            self.qLabelFoundResults.setHidden(False)
            # show buttons
            self.qPushButtonFindPrevious.setHidden(False)
            self.qPushButtonFindNext.setHidden(False)

            self.qPushButtonFindSql.setIcon(self.style().standardIcon(
                getattr(QtWidgets.QStyle, 'SP_DialogCancelButton')))

            # add actions
            self.qLineEditFindSql.textChanged.connect(
                lambda keyword: self.find_sql(keyword))
            self.qPushButtonFindPrevious.clicked.connect(
                lambda: self.sql_field.find(self.qLineEditFindSql.text(), QtGui.QTextDocument.FindBackward))
            self.qPushButtonFindNext.clicked.connect(
                lambda: self.sql_field.find(self.qLineEditFindSql.text()))
        else:
            # hide line edit
            self.qLineEditFindSql.clear()
            self.qLineEditFindSql.setHidden(True)

            self.qLabelFoundResults.clear()
            self.qLabelFoundResults.setHidden(True)
            # hide buttons
            self.qPushButtonFindPrevious.setHidden(True)
            self.qPushButtonFindNext.setHidden(True)

            self.qPushButtonFindSql.setIcon(self.style().standardIcon(
                getattr(QtWidgets.QStyle, 'SP_FileDialogContentsView')))

            # remove actions
            self.qLineEditFindSql.textChanged.disconnect()
            self.qPushButtonFindPrevious.clicked.disconnect()
            self.qPushButtonFindNext.clicked.disconnect()

    def find_sql(self, keyword):
        """
        Finds keyword in sql field and counts occurrences.
        """
        self.qLabelFoundResults.clear()
        if len(keyword) > 0:
            count = self.sql_field.toPlainText().lower().count(keyword.lower())
            self.qLabelFoundResults.setText(f"{count} result" + ("s" if count != 1 else ""))
        self.sql_field.find(keyword)

    def open_sql_query(self):
        """
        Opens a SQL file and displays it in the sql field.
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open SQL Query File", "",
                                                            "SQL Files (*.sql);;Text Files (*.txt);;All Files (*)", options=options)

        if fileName:
            filename = (f'{fileName}.sql' if fileName.split('.')[-1] != 'sql' else fileName)
            self.log.info("Opening SQL query: %s", filename)
            with open(filename, 'r') as file:
                sql = file.read()
                self.sql_field.setPlainText(sql)

    def save_sql_query(self):
        """
        Saves current query from the sql field to a SQL file.
        """
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save current SQL query as a File", "",
                                                            "SQL Files (*.sql);;All Files (*)", options=options)

        if fileName:
            filename = (f'{fileName}.sql' if fileName.split('.')[-1] != 'sql' else fileName)
            with open(filename, 'w+') as file:
                data = self.sql_field.toPlainText()
                file.write(data)
            self.log.info("SQL query saved as: %s", filename)

    def insert_sql(self):
        self.sql_field.clear()
        df_columns = (f'"{col}"' for col in self.parent().parent().get_current_df().columns.to_list())
        columns = f'({", ".join(df_columns)})'
        table = self.parent().parent().pandas_dataview.combo.currentText()

        if table == 'SQL':
            table = '<table_name>'
            columns = ''

        sql = f"INSERT INTO {table} {columns} \nVALUES();"
        self.sql_field.setPlainText(sql)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_extension = pathlib.Path(file_path).suffix

            if file_extension == '.sql' or file_extension == '.txt':
                self.log.info("Loading SQL file into GUI: %s", file_path)
                with open(file_path, 'r') as file:
                    data = file.read()
                    self.set_sql(data)

            else:
                self.log.error(f'{file_extension} is not supported.')
