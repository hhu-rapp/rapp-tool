import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from rapp import gui
from rapp.gui.pipeline import Pipeline
from rapp.gui.xai import XAI
from rapp.gui.faml import FairML

# rapp machine learning
from rapp.pipeline import MLPipeline


class Tabs(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(Tabs, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()

    def initUI(self):
        # create layout
        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vLayout)

        # create widgets
        self.tab = QtWidgets.QTabWidget()
        self.MLTab = Pipeline()
        self.XAITab = XAI()
        self.FairnessTab = FairML()

        # add widgets to tab
        self.tab.addTab(self.MLTab, 'Pipeline Settings')
        self.tab.addTab(self.XAITab, 'Explainable AI')
        self.tab.addTab(self.FairnessTab, 'Fairness-Aware ML')

        # add widgets to layout
        vLayout.addWidget(self.tab, 3)
        vLayout.addWidget(self.qmainwindow.loggingTextBrowser, 1)
