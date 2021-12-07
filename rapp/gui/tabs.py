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


class Tabs(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(Tabs, self).__init__()

        self.initUI()

    def initUI(self):
        # create widgets
        self.MLTab = Pipeline()
        self.XAITab = XAI()
        self.FairnessTab = FairML()

        # add widgets
        self.addTab(self.MLTab, 'Pipeline Settings')
        self.addTab(self.XAITab, 'Explainable AI')
        self.addTab(self.FairnessTab, 'Fairness-Aware ML')