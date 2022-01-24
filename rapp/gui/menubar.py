import logging
import os
import traceback
from configparser import ConfigParser, MissingSectionHeaderError

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

        # add entries to the menu
        self.menuFile.addAction(self.actionOpen_Database)
        self.menuFile.addMenu(self.menuSql)
        self.menuSql.addAction(self.actionOpen_SQLite_Query)
        self.menuSql.addAction(self.actionSave_SQLite_Query)
        self.menuFile.addAction(self.actionLoad_Config)
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

        self.actionCopy.setText(_translate("Window", "Copy"))
        self.actionPaste.setText(_translate("Window", "Paste"))

    def initMenuAction(self):
        # file
        self.actionOpen_Database.triggered.connect(self.openDatabase)
        self.actionOpen_SQLite_Query.triggered.connect(self.openSQLQuery)
        self.actionSave_SQLite_Query.triggered.connect(self.saveSQLQuery)
        self.actionLoad_Config.triggered.connect(self.loadConfigurationFile)

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
            logging.info("Loading SQL file into GUI: %s", fileName)
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
            config = ConfigParser()

            try:
                config.read(fileName)
            except MissingSectionHeaderError as e:
                msg = gui.helper.timeLogMsg(".ini File is missing ['Files'] and ['Settings'] Headers")
                traceback.print_exc()

                self.qMainWindow.qmainwindow.loggingTextBrowser.append(msg)
                return

            # load db
            if 'filename' in config['Files']:
                db_path = config['Files']['filename']
                self.qMainWindow.connectDatabase(os.path.normpath(db_path))

            # open and execute sql query
            if 'sql_filename' in config['Files']:
                with open(config['Files']['sql_filename'], 'r') as file:
                    data = file.read()
                    self.qMainWindow.sqlTbox.setPlainText(data)
                    self.qMainWindow.displaySql(data)

            # load settings
            # TODO: Load other settings
            # TODO: Better way to access MLTab attributes
            if 'label_name' in config['Settings']:
                target = config['Settings']['label_name']
                self.qMainWindow.qmainwindow.tabs.MLTab.cbName.setCurrentText(target)

            if 'type' in config['Settings']:
                type = config['Settings']['type']
                self.qMainWindow.qmainwindow.tabs.MLTab.cbType.setCurrentText(type)

            # TODO: better way split string
            if 'estimators' in config['Settings']:
                estimators = config['Settings']['estimators']
                estimators_list = estimators.replace('[','').replace(']', '')
                estimators_list = estimators_list.replace(' ', '')

                self.qMainWindow.qmainwindow.tabs.MLTab.cbEstimator.check_items(estimators_list.split(','))

            if 'sensitive_attributes' in config['Settings']:
                sensitive_attributes = config['Settings']['sensitive_attributes']
                s_attributes_list = sensitive_attributes.replace('[','').replace(']', '')
                s_attributes_list = s_attributes_list.replace(' ', '')

                self.qMainWindow.qmainwindow.tabs.MLTab.cbSAttributes.check_items(s_attributes_list.split(','))

    def copySQLQuery(self):
        QApplication.clipboard().setText(self.qMainWindow.sqlTbox.toPlainText())

    def pasteSQLQuery(self):
        text = QApplication.clipboard().text()
        self.qMainWindow.sqlTbox.setPlainText(text)
