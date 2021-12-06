import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets


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
        self.addAction(self.menuFile.menuAction())
        self.addAction(self.menuEdit.menuAction())

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Window", "MainWindow"))
        self.menuFile.setTitle(_translate("Window", "&File"))
        self.menuEdit.setTitle(_translate("Window", "&Edit"))

        self.actionOpen_Database.setText(_translate("Window", "Open Database"))
        self.actionOpen_Database.setStatusTip(_translate(
            "Window", "Opens SQLite Database. File type is \'.db\'"))
        self.actionOpen_Database.setShortcut(_translate("Window", "Ctrl+O"))

        self.actionOpen_SQLite_Query.setText(
            _translate("Window", "Open SQLite Query"))
        self.actionOpen_SQLite_Query.setStatusTip(
            _translate("Window", "Opens an SQLite query file"))
        self.actionOpen_SQLite_Query.setShortcut(_translate("Window", "Ctrl+Shift+O"))

        self.actionCopy.setText(_translate("Window", "Copy"))
        self.actionPaste.setText(_translate("Window", "Paste"))

    def initMenuAction(self):
        # file
        self.actionOpen_SQLite_Query.triggered.connect(self.openSQLQuery)
        self.actionOpen_Database.triggered.connect(self.openDatabase)

    def openDatabase(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                            "Database Files (*.db);;All Files (*)", options=options)
        if fileName:
            print(os.path.normpath(fileName))

            self.qMainWindow.connectDatabase(os.path.normpath(fileName))

    def openSQLQuery(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                            "Database Files (*.sql);;All Files (*)", options=options)

        if fileName:
            with open(fileName, 'r') as file:
                data = file.read()
                self.qMainWindow.sqlTbox.setPlainText(data)
