import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.widgets.interpretability_views import InitialView, ModelViewCLF, ModelViewREG, SampleView
from rapp.util import estimator_name


class InterpretabilityWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(InterpretabilityWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.current_view = None
        self.initUI()

        self.button_header_layout = QtWidgets.QHBoxLayout()
        self.model_list_button = QtWidgets.QPushButton('Zurück : Model List')
        self.model_list_button.clicked.connect(self._load_initial_view)
        self.model_list_button.setStatusTip('Go back to model list')
        self.model_list_button.resize(50, 50)

        self.button_header_layout = QtWidgets.QHBoxLayout()
        self.model_insight_button = QtWidgets.QPushButton('Zurück : Model Insights')
        self.model_insight_button.clicked.connect(self._load_model_view)
        self.model_insight_button.setStatusTip('Go back to model insights')
        self.model_insight_button.resize(50, 50)

        self.selected_model_label = QtWidgets.QLabel()

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
        self.current_view.clear_widget()
        self._clear_button_header()

        self.current_view = self.initial_view

        self.main_layout.addWidget(self.current_view)

    def _load_model_view(self, model_idx):
        self.current_view.clear_widget()
        self._clear_button_header()

        models = list(self.pipeline.performance_results.keys())

        self.selected_model_label.setText(f'Model : {estimator_name(models[model_idx])}')

        if self.pipeline.type == 'classification':
            self.model_view = ModelViewCLF(self.pipeline, models[model_idx], self._load_sample_view,
                                           self.current_view.get_mode_idx())

        if self.pipeline.type == 'regression':
            self.model_view = ModelViewREG(self.pipeline, models[model_idx], self._load_sample_view,
                                           self.current_view.get_mode_idx())

        self.current_view = self.model_view

        # add to layout
        self.button_header_layout.addWidget(self.model_list_button)
        self.button_header_layout.addWidget(self.selected_model_label)
        self.main_layout.addLayout(self.button_header_layout)
        self.main_layout.addWidget(self.current_view)

    def _load_sample_view(self):
        df = self.current_view.get_selected_df()
        self.current_view.clear_widget()
        self._clear_button_header()

        self.sample_view = SampleView(self.pipeline, df, self.current_view.get_mode_idx())

        self.current_view = self.sample_view

        # add to layout
        self.button_header_layout.addWidget(self.model_list_button)
        self.button_header_layout.addWidget(self.model_insight_button)
        self.main_layout.addLayout(self.button_header_layout)
        self.main_layout.addWidget(self.current_view)

    def _clear_button_header(self):
        self.model_list_button.setParent(None)
        self.selected_model_label.setParent(None)
        self.model_insight_button.setParent(None)
