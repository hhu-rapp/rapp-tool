import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from rapp import gui
from rapp.gui.pipeline import Pipeline


class SimpleSettings(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(SimpleSettings, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()

    def initUI(self):
        # create layout
        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vLayout)

        # create widgets
        self.tab = QtWidgets.QTabWidget()
        self.simple_tab = Pipeline(self.qmainwindow)

        # add widgets to tab
        self.tab.addTab(self.simple_tab, 'Simple Settings')

        # add widgets to layout
        vLayout.addWidget(self.tab, 3)
        vLayout.addWidget(self.qmainwindow.loggingTextBrowser, 1)
