# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.helper import CheckableComboBox
from rapp.gui.widgets import DatasetTable, OverviewTable, IndividualPerformanceTable, IndividualFairnessTable
from rapp.util import estimator_name


class FairnessWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(FairnessWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()

    def initUI(self):
        # create layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(layout)

        # create widgets
        self.tabs = QtWidgets.QTabWidget()

        self.sensitiveDatasetTable = []
        self.sensitiveIndividualTable = []

        self.__init_dataset_tab()
        self.__init_overview_tab()
        self.__init_individual_tab()

        # add widgets to layout
        layout.addWidget(self.tabs)

    def __init_dataset_tab(self):
        # create layout
        self.dataset_tab = QtWidgets.QWidget()
        self.dataset_tab.setLayout(QtWidgets.QVBoxLayout())

        # add to layout
        self.tabs.addTab(self.dataset_tab, 'Dataset')

    def __init_overview_tab(self):
        # create layout
        self.overview_tab = QtWidgets.QWidget()
        self.overview_tab.setLayout(QtWidgets.QVBoxLayout())

        # add to layout
        self.tabs.addTab(self.overview_tab, 'Model Summary')

    def __init_individual_tab(self):
        # create layout
        self.individual_tab = QtWidgets.QWidget()
        self.individual_tab.setLayout(QtWidgets.QVBoxLayout())

        # add to layout
        tab_idx = self.tabs.addTab(self.individual_tab, 'Model Inspection')
        self.individual_tab_idx = tab_idx

    def populate_fairness_tabs(self, pipeline, data_settings):
        """
		Parameters
		----------
		pipeline: rapp.pipeline object
			A pipeline object with trained models.

		It is expected that the object has following attributes:
		data, sensitive_attributes, score_functions, statistics_results,
		fairness_functions, performance_results, fairness_results, type.

		data_settings: dict
			It represents the loaded data in the pipeline, it has the form:
			{'studies_id': studies_id of train data,
			'features_id': features_id of train data,
			'labels_id': predicting label_id of the model}
		"""
        self.pipeline = pipeline
        self.data_settings = data_settings

        self.refresh_tabs()
        self.populate_dataset_tab()
        self.populate_overview_tab()
        self.populate_individual_tab()

    def populate_dataset_tab(self):
        pl_type = self.pipeline.type
        # one groupBox per sensitive attribute
        for i, sensitive in enumerate(self.pipeline.sensitive_attributes):
            self.sensitiveDatasetTable.append(
                DatasetTable(sensitive, self.pipeline.data, self.pipeline.statistics_results,
                             self.data_settings))

            if pl_type == "classification":
                self.sensitiveDatasetTable[i].populate_table()
            if pl_type == "regression":
                self.sensitiveDatasetTable[i].populate_plot()

            # add to layout
            self.dataset_tab.layout().addWidget(self.sensitiveDatasetTable[i])

    def clear_dataset_table(self):
        for widget in self.sensitiveDatasetTable:
            widget.setParent(None)
        self.sensitiveDatasetTable = []

    def populate_overview_tab(self):
        pl_type = self.pipeline.type.capitalize()
        # comboBox for filtering
        self.cbPerformance = CheckableComboBox()
        self.cbFairness = CheckableComboBox()
        self.cbOverviewModes = QtWidgets.QComboBox()
        self.cbSenstitiveAttributes = QtWidgets.QComboBox()

        # groupBox for the filters
        self.overview_metrics_groupBox = QGroupBox("Filters")
        self.overview_metrics_groupBox.size()
        overviewTopLayout = QtWidgets.QFormLayout()
        self.overview_metrics_groupBox.setLayout(overviewTopLayout)

        # load comboBoxes
        performance_metrics = list(self.pipeline.score_functions.keys())
        for metric in performance_metrics:
            self.cbPerformance.addItem(str(metric))
        self.cbPerformance.check_items(performance_metrics)

        fairness_notions = list(self.pipeline.fairness_functions.keys())
        for notion in fairness_notions:
            self.cbFairness.addItem(str(notion))
        self.cbFairness.check_items(fairness_notions)

        modes = list(self.pipeline.data.keys())
        for mode in modes:
            self.cbOverviewModes.addItem(str(mode).capitalize())

        for sensitive in self.pipeline.sensitive_attributes:
            self.cbSenstitiveAttributes.addItem(str(sensitive).capitalize())

        self.cbPerformance.currentIndexChanged.connect(self.populate_overview_table)
        self.cbFairness.currentIndexChanged.connect(self.populate_overview_table)
        self.cbOverviewModes.currentIndexChanged.connect(self.populate_overview_table)
        self.cbSenstitiveAttributes.currentIndexChanged.connect(self.populate_overview_table)

        # add to groupBox
        overviewTopLayout.addRow(f"{pl_type} Metrics:", self.cbPerformance)
        overviewTopLayout.addRow('Fairness Metrics:', self.cbFairness)
        overviewTopLayout.addRow('Mode:', self.cbOverviewModes)
        overviewTopLayout.addRow('Sensitive Attribute:', self.cbSenstitiveAttributes)

        # add to layout
        self.overview_tab.layout().addWidget(self.overview_metrics_groupBox)
        self.populate_overview_table()

    def clear_overview_table(self):
        try:
            self.overview_groupBox.setParent(None)
        except AttributeError:
            return

    def populate_overview_table(self):
        self.clear_overview_table()
        # get values from filters
        mode = self.cbOverviewModes.currentText().lower()
        sensitive = self.cbSenstitiveAttributes.currentText()
        performance_metrics = self.cbPerformance.get_checked_items()
        fairness_notions = self.cbFairness.get_checked_items()
        metrics = self.cbPerformance.get_checked_items()
        metrics.extend(fairness_notions)

        models = list(self.pipeline.performance_results.keys())
        pl_type = self.pipeline.type

        # create groupBox
        self.overview_groupBox = OverviewTable(mode, models, metrics, pl_type, performance_metrics,
                                               self.pipeline.performance_results, fairness_notions,
                                               self.pipeline.fairness_results, sensitive,
                                               )
        self.overview_groupBox.set_model_click_function(self.open_individual_tab)

        # add to layout
        self.overview_tab.layout().addWidget(self.overview_groupBox)

    def populate_individual_tab(self):
        # comboBox for filtering
        self.cbModels = QtWidgets.QComboBox()
        self.individual_cbMetrics = QtWidgets.QComboBox()

        # groupBox for the filters
        self.individual_metrics_groupBox = QGroupBox("Filters")
        individualTopLayout = QtWidgets.QFormLayout()
        self.individual_metrics_groupBox.setLayout(individualTopLayout)

        # load comboBoxes
        for model in self.pipeline.performance_results:
            self.cbModels.addItem(estimator_name(model))
        self.individual_cbMetrics.addItem("Performance")
        self.individual_cbMetrics.addItem("Fairness")

        self.individual_cbMetrics.currentIndexChanged.connect(self.populate_individual_table)
        self.cbModels.currentIndexChanged.connect(self.populate_individual_table)

        # add to groupBox
        individualTopLayout.addRow('Model:', self.cbModels)
        individualTopLayout.addRow('Metrics:', self.individual_cbMetrics)

        # add to layout
        self.individual_tab.layout().addWidget(self.individual_metrics_groupBox)
        self.populate_individual_table()

    def populate_individual_table(self):
        self.clear_individual_table()
        # get values from filters
        metric_type = self.individual_cbMetrics.currentText()

        model_idx = self.cbModels.currentIndex()
        models = list(self.pipeline.performance_results.keys())
        model = models[model_idx]

        pl_type = self.pipeline.type
        if metric_type == "Performance":
            self.individualPerformanceTable = IndividualPerformanceTable(self.pipeline.data, model,
                                                                         self.pipeline.performance_results)

            # add to layout
            self.individual_tab.layout().addWidget(self.individualPerformanceTable)
        if metric_type == "Fairness":
            for i, sensitive in enumerate(self.pipeline.sensitive_attributes):
                self.sensitiveIndividualTable.append(IndividualFairnessTable(self.pipeline.data, model,
                                                                             self.pipeline.fairness_results, sensitive,
                                                                             pl_type))

                # add to layout
                self.individual_tab.layout().addWidget(self.sensitiveIndividualTable[i])

    def clear_individual_table(self):
        try:
            for widget in self.sensitiveIndividualTable:
                widget.setParent(None)
            self.sensitiveIndividualTable = []
            self.individualPerformanceTable.setParent(None)
        except AttributeError:
            return

    def refresh_tabs(self):
        try:
            self.individual_metrics_groupBox.setParent(None)
            self.overview_metrics_groupBox.setParent(None)
        except AttributeError:
            return

        self.clear_dataset_table()
        self.clear_overview_table()
        self.clear_individual_table()

    def open_individual_tab(self, model_index):
        self.tabs.setCurrentIndex(self.individual_tab_idx)
        self.cbModels.setCurrentIndex(model_index)
