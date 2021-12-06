# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets


class MLTab(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        super(MLTab, self).__init__()
        self.initUI()

    def initUI(self):
        # create widgets
        self.MLTab = QtWidgets.QWidget()
        self.XAITab = QtWidgets.QWidget()
        self.FairnessTab = QtWidgets.QWidget()

        # add widgets
        self.addTab(self.MLTab, 'Pipeline Settings')
        self.addTab(self.XAITab, 'Explainable AI')
        self.addTab(self.FairnessTab, 'Fairness-Aware ML')

    def initMLTab(self):
        pass

    def initXAITab(self):
        pass

    def initFairnessTab(self):
        pass
