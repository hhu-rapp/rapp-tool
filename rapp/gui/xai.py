import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp
from rapp import gui


class XAI(QtWidgets.QWidget):

    def __init__(self):
        super(XAI, self).__init__()
