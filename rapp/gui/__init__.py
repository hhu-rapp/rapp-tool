# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
# theme
from qt_material import apply_stylesheet

# dataframe
from rapp.gui.dbview import DataView

# import rapp gui widgets
from rapp.gui.helper import Color
from rapp.gui.menubar import MenuBar
from rapp.gui.dbview import DatabaseLayoutWidget
from rapp.gui.tabs import Tabs

db_filepath = "data/rapp.db"
sql_temp_path = "sql_temp.sql"


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # variables before initializing gui
        self.__conn = None # Database connection.
        self.filepath_db = db_filepath

        # widgets before initializing gui
        self.loggingTextBrowser = QtWidgets.QTextBrowser()

        # apply_stylesheet(self, theme='dark_blue.xml')
        self.initUI()
        self.initLayout()

        self.menubar = MenuBar(self.databaseLayoutWidget)
        self.setMenuBar(self.menubar)

        # set status bar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def initUI(self):
        # set the title
        self.setWindowTitle('Responsible Performance Prediction [Demoversion]')

        # setting the geometry of window
        self.width = 1280
        self.height = 800
        self.setGeometry(100, 60, self.width, self.height)

    def initLayout(self):
        skeletonWidget = QtWidgets.QWidget()
        skeletonLayout = QtWidgets.QHBoxLayout()
        skeletonWidget.setLayout(skeletonLayout)
        self.setCentralWidget(skeletonWidget)

        # create widgets
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.databaseLayoutWidget = DatabaseLayoutWidget(self, self.filepath_db)
        tabs = Tabs(self)

        # add widgets
        splitter.addWidget(self.databaseLayoutWidget)
        splitter.addWidget(tabs)
        splitter.setSizes([800, 480])
        skeletonLayout.addWidget(splitter)
