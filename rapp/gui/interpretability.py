import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.widgets.evaluation_views import InitialView, ModelView
from rapp.util import estimator_name


class InterpretabilityWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(InterpretabilityWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.current_view = None
        self.initUI()

    def initUI(self):
        # create layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.main_layout)

    def initialize_tab(self, pipeline):
        """
        Parameters
        ----------
        pipeline: rapp.pipeline object
            A pipeline object with trained models.

        """
        if self.current_view is not None:
            self._load_initial_view()
            self.current_view.clear_widget()

        self.pipeline = pipeline
        self.initial_view = InitialView(self.pipeline, self._load_model_view)
        self.current_view = self.initial_view

        self.main_layout.addWidget(self.current_view)

    def _load_initial_view(self):
        self.current_view.setParent(None)
        self.current_view = self.initial_view

        self.main_layout.addWidget(self.current_view)

