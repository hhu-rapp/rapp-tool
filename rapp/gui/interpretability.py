import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from rapp import gui
from rapp.gui.pipeline import Pipeline


class InterpretabilityWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(InterpretabilityWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()

    def initUI(self):
        # create layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
