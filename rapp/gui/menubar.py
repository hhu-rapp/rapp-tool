import logging
log = logging.getLogger('GUI')
import os
import traceback
from rapp.parser import RappConfigParser

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.Qt import QApplication, QClipboard

from rapp import gui


class MenuBar(QtWidgets.QMenuBar):

    def __init__(self, qMainWindow):
        super(MenuBar, self).__init__()

        self.qMainWindow = qMainWindow
        self.initMenu()
        self.retranslateUi()
        self.initMenuAction()

    def initMenu(self):
        self.setGeometry(QtCore.QRect(0, 0, 1280, 24))
        self.setObjectName("menubar")

        # Menu
        self.menuFile = QtWidgets.QMenu(self)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self)
        self.menuEdit.setObjectName("menuEdit")
        self.menuSql = QtWidgets.QMenu(self)
        self.menuSql.setObjectName("menuSql")

        # setting actions for the menu
        # File
        self.actionOpen_Database = QtWidgets.QAction(self)
        self.actionOpen_Database.setObjectName("actionOpen_Database")
        self.actionLoad_Config = QtWidgets.QAction(self)
        self.actionLoad_Config.setObjectName("actionLoad_Config")
        self.actionSave_Config = QtWidgets.QAction(self)
        self.actionSave_Config.setObjectName("actionSave_Config")

        # Sql
        self.actionOpen_SQLite_Query = QtWidgets.QAction(self)
        self.actionOpen_SQLite_Query.setObjectName("actionOpen_SQLite_Query")
        self.actionSave_SQLite_Query = QtWidgets.QAction(self)
        self.actionSave_SQLite_Query.setObjectName("actionSave_SQLite_Query")

        # Edit
        self.actionCopy = QtWidgets.QAction(self)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(self)
        self.actionPaste.setObjectName("actionPaste")

        # add entries to the file menu
        self.menuFile.addAction(self.actionLoad_Config)
        self.menuFile.addAction(self.actionSave_Config)
        self.menuFile.addAction(self.actionOpen_Database)
        self.menuFile.addMenu(self.menuSql)
        self.menuSql.addAction(self.actionOpen_SQLite_Query)
        self.menuSql.addAction(self.actionSave_SQLite_Query)

        # Edit
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)

        # adding to menubar
        self.addAction(self.menuFile.menuAction())
        self.addAction(self.menuEdit.menuAction())

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Window", "MainWindow"))
        self.menuFile.setTitle(_translate("Window", "&File"))
        self.menuEdit.setTitle(_translate("Window", "&Edit"))
        self.menuSql.setTitle(_translate("Window", "SQL Query"))

        self.actionOpen_Database.setText(_translate("Window", "Open Database"))
        self.actionOpen_Database.setStatusTip(_translate(
            "Window", "Opens SQLite Database. File type is \'.db\'"))
        self.actionOpen_Database.setShortcut(_translate("Window", "Ctrl+O"))

        self.actionOpen_SQLite_Query.setText(
            _translate("Window", "Open SQLite Query"))
        self.actionOpen_SQLite_Query.setStatusTip(
            _translate("Window", "Opens an SQLite query file"))
        self.actionOpen_SQLite_Query.setShortcut(_translate("Window", "Ctrl+Shift+O"))

        self.actionSave_SQLite_Query.setText(
            _translate("Window", "Save SQLite Query"))
        self.actionSave_SQLite_Query.setStatusTip(
            _translate("Window", "Saves an SQLite query"))
        self.actionSave_SQLite_Query.setShortcut(_translate("Window", "Ctrl+Shift+S"))

        self.actionLoad_Config.setText(
            _translate("Window", "Open Config File"))
        self.actionLoad_Config.setStatusTip(
            _translate("Window", "Opens a Config File"))
        self.actionLoad_Config.setShortcut(_translate("Window", "Ctrl+Shift+C"))

        self.actionSave_Config.setText(
            _translate("Window", "Save Config File"))
        self.actionSave_Config.setStatusTip(
            _translate("Window", "Saves a Config File"))
        self.actionSave_Config.setShortcut(_translate("Window", "Ctrl+Shift+V"))

        self.actionCopy.setText(_translate("Window", "Copy"))
        self.actionPaste.setText(_translate("Window", "Paste"))
        self.actionCopy.setText(_translate("Window", "Copy SQL"))
        self.actionPaste.setText(_translate("Window", "Paste SQL"))

    def initMenuAction(self):
        # file
        self.actionOpen_Database.triggered.connect(self.openDatabase)
        self.actionOpen_SQLite_Query.triggered.connect(self.openSQLQuery)
        self.actionSave_SQLite_Query.triggered.connect(self.saveSQLQuery)
        self.actionLoad_Config.triggered.connect(self.loadConfigurationFile)
        self.actionSave_Config.triggered.connect(self.saveConfigurationFile)

        self.actionCopy.triggered.connect(self.copySQLQuery)
        self.actionPaste.triggered.connect(self.pasteSQLQuery)

    def openDatabase(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open SQLite Database File", "",
                                                            "Database Files (*.db);;All Files (*)", options=options)
        if fileName:
            print(os.path.normpath(fileName))

            self.qMainWindow.connectDatabase(os.path.normpath(fileName))

    def openSQLQuery(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open SQLite Query File", "",
                                                            "Database Files (*.sql);;All Files (*)", options=options)

        if fileName:
            with open(fileName, 'r') as file:
                data = file.read()
                self.qMainWindow.load_sql(data)

    def saveSQLQuery(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save SQL Query as a File", "",
                                                            "Database Files (*.sql);;All Files (*)", options=options)

        if fileName:
            log.info("Loading SQL file into GUI: %s", fileName)
            with open(fileName, 'w+') as file:
                data = self.qMainWindow.sqlTbox.toPlainText()
                file.write(data)

    def loadConfigurationFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Config File", "",
                                                            "Configuration Files (*.ini);;All Files (*)",
                                                            options=options)

        if fileName:
            parser = RappConfigParser()

            try:
                cf = parser.parse_file(fileName)
            except Exception as e:
                log.error(traceback.format_exc())
                traceback.print_exc()
                return

            # load required settings

            self.qMainWindow.connectDatabase(os.path.normpath(cf.filename))

            self.qMainWindow.qmainwindow.tabs.MLTab.cbType.setCurrentText(cf.type.capitalize())

            if hasattr(cf, 'sql_file') and cf.sql_file is not None:
                with open(cf.sql_file, 'r') as f:
                    sql = f.read()
                    self.qMainWindow.sql_tabs.displaySql(sql)
                    self.qMainWindow.sql_tabs.set_sql(sql)

            elif hasattr(cf, 'sql_query') and cf.sql_query is not None:
                sql = cf.sql_query
                self.qMainWindow.sql_tabs.displaySql(sql)
                self.qMainWindow.sql_tabs.set_sql(sql)

            else:
                self.qMainWindow.sql_tabs.featuresSelect.setCurrentText(f"{cf.studies_id}_{cf.features_id}")
                self.qMainWindow.sql_tabs.targetSelect.setCurrentText(cf.labels_id)
                self.qMainWindow.sql_tabs.load_selected_sql_template()

            # load optional settings
            # TODO: Better way to access MLTab attributes
            if hasattr(cf, 'label_name'):
                self.qMainWindow.qmainwindow.tabs.MLTab.cbName.setCurrentText(cf.label_name)

            if hasattr(cf, 'sensitive_attributes'):
                self.qMainWindow.qmainwindow.tabs.MLTab.cbSAttributes.check_items(cf.sensitive_attributes)

            if hasattr(cf, 'report_path'):
                self.qMainWindow.qmainwindow.tabs.MLTab.lePath.setText(cf.report_path)

            if hasattr(cf, 'estimators'):
                self.qMainWindow.qmainwindow.tabs.MLTab.cbEstimator.check_items(cf.estimators)

    def saveConfigurationFile(self):
        pass

    def copySQLQuery(self):
        QApplication.clipboard().setText(self.qMainWindow.sqlTbox.toPlainText())
        QApplication.clipboard().setText(self.qMainWindow.sql_tabs.sql_field.toPlainText())

    def pasteSQLQuery(self):
        text = QApplication.clipboard().text()
        self.qMainWindow.sqlTbox.setPlainText(text)
        self.qMainWindow.sql_tabs.sql_field.setPlainText(text)
        # Change to advanced tab.
        self.qMainWindow.sql_tabs.tabs.setCurrentIndex(self.qMainWindow.sql_tabs._advanced_tab_index)
