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

    def __init__(self, databaseLayoutWidget):
        super(MenuBar, self).__init__()

        self.databaseLayoutWidget = databaseLayoutWidget
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
        self.menuDatabase = QtWidgets.QMenu(self)
        self.menuDatabase.setObjectName("menuDatabase")

        # setting actions for the menu
        # File
        self.actionOpen_Pipeline_Database = QtWidgets.QAction(self)
        self.actionOpen_Pipeline_Database.setObjectName("actionOpen_Pipeline_Database")
        self.actionOpen_Prediction_Database = QtWidgets.QAction(self)
        self.actionOpen_Prediction_Database.setObjectName("actionOpen_Prediction_Database")

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
        self.menuFile.addMenu(self.menuDatabase)
        self.menuDatabase.addAction(self.actionOpen_Pipeline_Database)
        self.menuDatabase.addAction(self.actionOpen_Prediction_Database)
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
        self.menuDatabase.setTitle(_translate("Window", "Database"))

        self.actionOpen_Pipeline_Database.setText(_translate("Window", "Open Pipeline Database"))
        self.actionOpen_Pipeline_Database.setStatusTip(_translate(
            "Window", "Opens SQLite Database. File type is \'.db\'"))
        self.actionOpen_Pipeline_Database.setShortcut(_translate("Window", "Ctrl+O"))

        self.actionOpen_Prediction_Database.setText(_translate("Window", "Open Prediction Database"))
        self.actionOpen_Prediction_Database.setStatusTip(_translate(
            "Window", "Opens SQLite Database. File type is \'.db\'"))
        self.actionOpen_Prediction_Database.setShortcut(_translate("Window", "Ctrl+Alt+O"))

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
        self.actionOpen_Pipeline_Database.triggered.connect(self.openDatabasePipeline)
        self.actionOpen_Prediction_Database.triggered.connect(self.openDatabasePrediction)
        self.actionOpen_SQLite_Query.triggered.connect(self.openSQLQuery)
        self.actionSave_SQLite_Query.triggered.connect(self.saveSQLQuery)
        self.actionLoad_Config.triggered.connect(self.showConfigurationFileDialog)
        self.actionSave_Config.triggered.connect(self.saveConfigurationFile)

        self.actionCopy.triggered.connect(self.copySQLQuery)
        self.actionPaste.triggered.connect(self.pasteSQLQuery)

    def openDatabasePipeline(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open SQLite Database File for Training", "",
                                                            "Database Files (*.db);;All Files (*)", options=options)
        if fileName:
            self.databaseLayoutWidget.connectDatabase(os.path.normpath(fileName))

    def openDatabasePrediction(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open SQLite Database File for Prediction", "",
                                                            "Database Files (*.db);;All Files (*)", options=options)
        if fileName:
            a = self.parent().databasePredictionLayoutWidget.connectDatabase(os.path.normpath(fileName))

    def openSQLQuery(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open SQLite Query File", "",
                                                            "Database Files (*.sql);;All Files (*)", options=options)

        if fileName:
            with open(fileName, 'r') as file:
                data = file.read()
                self.databaseLayoutWidget.load_sql(data)

    def saveSQLQuery(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save SQL Query as a File", "",
                                                            "Database Files (*.sql);;All Files (*)", options=options)

        if fileName:
            log.info("Loading SQL file into GUI: %s", fileName)
            with open(fileName, 'w+') as file:
                data = self.databaseLayoutWidget.sqlTbox.toPlainText()
                file.write(data)

    def showConfigurationFileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Config File", "",
                                                            "Configuration Files (*.ini);;All Files (*)",
                                                            options=options)
        if fileName:
            self.loadConfigurationFile(fileName)

    def loadConfigurationFile(self, fileName):
        parser = RappConfigParser()

        try:
            cf = parser.parse_file(fileName)
        except Exception as e:
            log.error("Loading failed: " + str(e))
            return

        # load required settings

        self.databaseLayoutWidget.connectDatabase(os.path.normpath(cf.filename))

        self.databaseLayoutWidget.qmainwindow.settings.simple_tab.cbType.setCurrentText(cf.type.capitalize())

        if hasattr(cf, 'sql_file') and cf.sql_file is not None:
            with open(cf.sql_file, 'r') as f:
                sql = f.read()
                self.databaseLayoutWidget.sql_tabs.displaySql(sql)
                self.databaseLayoutWidget.sql_tabs.set_sql(sql)

        elif hasattr(cf, 'sql_query') and cf.sql_query is not None:
            sql = cf.sql_query
            self.databaseLayoutWidget.sql_tabs.displaySql(sql)
            self.databaseLayoutWidget.sql_tabs.set_sql(sql)

        else:
            self.databaseLayoutWidget.sql_tabs.featuresSelect.setCurrentText(f"{cf.studies_id}_{cf.features_id}")
            self.databaseLayoutWidget.sql_tabs.targetSelect.setCurrentText(cf.labels_id)
            self.databaseLayoutWidget.sql_tabs.load_selected_sql_template()

        # load optional settings
        # TODO: Better way to access MLTab attributes
        if hasattr(cf, 'label_name'):
            self.databaseLayoutWidget.qmainwindow.settings.simple_tab.cbName.setCurrentText(cf.label_name)

        if hasattr(cf, 'sensitive_attributes'):
            self.databaseLayoutWidget.qmainwindow.settings.simple_tab.cbSAttributes.check_items(cf.sensitive_attributes)

        if hasattr(cf, 'report_path'):
            self.databaseLayoutWidget.qmainwindow.settings.simple_tab.lePath.setText(cf.report_path)

        if hasattr(cf, 'estimators'):
            self.databaseLayoutWidget.qmainwindow.settings.simple_tab.cbEstimator.check_items(cf.estimators)

    def saveConfigurationFile(self):
        cf = self.databaseLayoutWidget.qmainwindow.settings.simple_tab.parse_settings()

        if cf is None:
            return

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Pipeline Settings as a File", "",
                                                            "Configuration Files (*.ini)", options=options)

        if fileName:
            with open(fileName + ".ini", 'w+') as file:
                config = vars(cf)

                if config["filename"] == None:
                    config["filename"] = "data/rapp/data.db"

                for key in config:
                    if key == "sql_df":
                        continue
                    if len(config[key]) == 0:
                        continue

                    file.write(key)
                    file.write("=")
                    file.write(str(config[key]))
                    file.write("\n")

            log.info("Saved pipeline settings as: %s.ini", fileName)

    def copySQLQuery(self):
        QApplication.clipboard().setText(self.databaseLayoutWidget.sql_tabs.sql_field.toPlainText())

    def pasteSQLQuery(self):
        text = QApplication.clipboard().text()
        self.databaseLayoutWidget.sql_tabs.sql_field.setPlainText(text)
        # Change to advanced tab.
        self.databaseLayoutWidget.sql_tabs.tabs.setCurrentIndex(self.databaseLayoutWidget.sql_tabs.advanced_tab_index)
