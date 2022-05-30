# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
# theme
from qt_material import apply_stylesheet

# dataframe
from rapp.gui.dbview import DataView

# import rapp gui widgets
from rapp.gui.prediction import PredictionWidget
from rapp.gui.fairness import FairnessWidget
from rapp.gui.XAI import XAIWidget
from rapp.gui.helper import Color
from rapp.gui.helper import LoggingTextBrowser, LoggingHandler
from rapp.gui.menubar import MenuBar
from rapp.gui.dbview import DatabaseLayoutWidget
from rapp.gui.settings import SimpleSettings

import logging
log = logging.getLogger("GUI")
log_pred = logging.getLogger("prediction")
log_pipeline = logging.getLogger("rapp.pipeline")

sql_temp_path = "sql_temp.sql"
sql_df = None


class Window(QMainWindow):
    def __init__(self, db_filepath="data/rapp/data.db"):
        super().__init__()
        
        # variables before initializing gui
        self.__conn = None  # Database connection.
        self.filepath_db = db_filepath
        self.sql_df = None
        
        # initialize logging handler
        self.loggingTextBrowser = LoggingTextBrowser()
        handler = LoggingHandler(self.loggingTextBrowser)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        log.addHandler(handler)
        log_pipeline.addHandler(handler)
        
        self.loggingTextBrowserPred = LoggingTextBrowser()
        handler_pred = LoggingHandler(self.loggingTextBrowserPred)
        handler_pred.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        log_pred.addHandler(handler_pred)
        
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
        self.tabs = QtWidgets.QTabWidget()

        self.__init_pipeline_settings_tab()
        self.__init_prediction_tab()
        self.__init_fairness_tab()
        self.__init_XAI_tab()

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(layout)
        self.setCentralWidget(self.tabs)
    
    def __init_pipeline_settings_tab(self):
        self.pipeline_settings = QtWidgets.QWidget()
        self.pipeline_settings.setLayout(QtWidgets.QHBoxLayout())
        
        # create widgets
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.databaseLayoutWidget = DatabaseLayoutWidget(self, self.filepath_db)
        self.settings = SimpleSettings(self)
        
        # add widgets
        splitter.addWidget(self.databaseLayoutWidget)
        splitter.addWidget(self.settings)
        splitter.setSizes([800, 480])
        self.pipeline_settings.layout().addWidget(splitter)
        
        self.tabs.addTab(self.pipeline_settings, 'Pipeline Settings')
    
    def __init_fairness_tab(self):
        self.fairness = QtWidgets.QWidget()
        self.fairness.setLayout(QtWidgets.QHBoxLayout())
        
        # create widgets
        self.fairness = FairnessWidget(self)
        
        # add widgets
        tab_idx = self.tabs.addTab(self.fairness, 'Fairness')
        self.fairness_tab_index = tab_idx
        self.tabs.setTabEnabled(tab_idx, False)
    
    def __init_XAI_tab(self):
        self.XAI = QtWidgets.QWidget()
        self.XAI.setLayout(QtWidgets.QHBoxLayout())
        
        # create widgets
        self.XAI = XAIWidget(self)
        
        # add widgets
        tab_idx = self.tabs.addTab(self.XAI, 'XAI')
        self.xai_tab_index = tab_idx
        self.tabs.setTabEnabled(tab_idx, False)

    def __init_prediction_tab(self):
        self.predictionWidget = QtWidgets.QWidget()
        self.predictionWidget.setLayout(QtWidgets.QHBoxLayout())

        # create widgets
        self.predictionWidget = PredictionWidget(self)

        # add widgets
        tab_idx = self.tabs.addTab(self.predictionWidget, 'Prediction')
        self.prediction_tab_index = tab_idx
        self.tabs.setTabEnabled(tab_idx, False)
