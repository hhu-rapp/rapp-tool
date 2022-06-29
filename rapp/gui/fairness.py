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
        self.sensitiveIndividualTables = []

        self.cbPerformance = None
        self.cbFairness = None
        self.cbOverviewModes = None
        self.cbSenstitiveAttributes = None
        self.overview_groupBox = None

        self.cbModels = None
        self.individual_cbMetrics = None
        self.individualPerformanceTable = None

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
        self._refresh_tabs()
        self._populate_dataset_tab(pipeline.data, pipeline.statistics_results,
                                   pipeline.sensitive_attributes,
                                   pipeline.type, data_settings)
        self._populate_overview_tab(pipeline)
        self._populate_individual_tab(pipeline)

    def _populate_dataset_tab(self, data, statistics_results, sensitive_attributes, pl_type, data_settings):
        # one collapsible box per sensitive attribute
        for i, sensitive in enumerate(sensitive_attributes):
            self.sensitiveDatasetTable.append(
                DatasetTable(sensitive, data, statistics_results, data_settings))

            if pl_type == "classification":
                self.sensitiveDatasetTable[i].populate_table()
            if pl_type == "regression":
                self.sensitiveDatasetTable[i].populate_plot()

            # add to layout
            self.dataset_tab.layout().addWidget(self.sensitiveDatasetTable[i])
        # add removable stretch
        self.stretch_dataset = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)
        self.dataset_tab.layout().addItem(self.stretch_dataset)

    def _clear_dataset_table(self):
        for widget in self.sensitiveDatasetTable:
            widget.setParent(None)
        self.sensitiveDatasetTable = []
        self.dataset_tab.layout().removeItem(self.stretch_dataset)

    def _populate_overview_tab(self, pipeline):
        pl_type = pipeline.type.capitalize()
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
        performance_metrics = list(pipeline.score_functions.keys())
        for metric in performance_metrics:
            self.cbPerformance.addItem(str(metric))
        self.cbPerformance.check_items(performance_metrics)

        fairness_notions = list(pipeline.fairness_functions.keys())
        for notion in fairness_notions:
            self.cbFairness.addItem(str(notion))
        self.cbFairness.check_items(fairness_notions)

        modes = list(pipeline.data.keys())
        for mode in modes:
            self.cbOverviewModes.addItem(str(mode).capitalize())

        for sensitive in pipeline.sensitive_attributes:
            self.cbSenstitiveAttributes.addItem(str(sensitive).capitalize())

        def populate_overview_table():
            self._populate_overview_table(pipeline.performance_results,
                                          pipeline.fairness_results, pipeline.type)

        self.cbPerformance.currentIndexChanged.connect(populate_overview_table)
        self.cbFairness.currentIndexChanged.connect(populate_overview_table)
        self.cbOverviewModes.currentIndexChanged.connect(populate_overview_table)
        self.cbSenstitiveAttributes.currentIndexChanged.connect(populate_overview_table)

        # add to groupBox
        overviewTopLayout.addRow(f"{pl_type} Metrics:", self.cbPerformance)
        overviewTopLayout.addRow('Fairness Metrics:', self.cbFairness)
        overviewTopLayout.addRow('Mode:', self.cbOverviewModes)
        overviewTopLayout.addRow('Sensitive Attribute:', self.cbSenstitiveAttributes)

        # add to layout
        self.overview_tab.layout().addWidget(self.overview_metrics_groupBox)
        self._populate_overview_table(pipeline.performance_results, pipeline.fairness_results, pipeline.type)

    def _clear_overview_table(self):
        try:
            self.overview_groupBox.setParent(None)
        except AttributeError:
            return

    def _populate_overview_table(self, performance_results, fairness_results, pl_type):
        self._clear_overview_table()
        # get values from filters
        mode = self.cbOverviewModes.currentText().lower()
        sensitive = self.cbSenstitiveAttributes.currentText()
        performance_metrics = self.cbPerformance.get_checked_items()
        fairness_notions = self.cbFairness.get_checked_items()
        metrics = self.cbPerformance.get_checked_items()
        metrics.extend(fairness_notions)

        models = list(performance_results.keys())


        # create groupBox
        self.overview_groupBox = OverviewTable(mode, models, metrics, pl_type, performance_metrics,
                                               performance_results, fairness_notions,
                                               fairness_results, sensitive)
        self.overview_groupBox.set_model_click_function(self.open_individual_tab)

        # add to layout
        self.overview_tab.layout().addWidget(self.overview_groupBox)

    def _populate_individual_tab(self, pipeline):
        # comboBox for filtering
        self.cbModels = QtWidgets.QComboBox()
        self.individual_cbMetrics = QtWidgets.QComboBox()

        # groupBox for the filters
        self.individual_metrics_groupBox = QGroupBox("Filters")
        individualTopLayout = QtWidgets.QFormLayout()
        self.individual_metrics_groupBox.setLayout(individualTopLayout)
        self.individual_metrics_groupBox.setAlignment(Qt.AlignTop)

        # load comboBoxes
        for model in pipeline.performance_results:
            self.cbModels.addItem(estimator_name(model))
        self.individual_cbMetrics.addItem("Performance")
        self.individual_cbMetrics.addItem("Fairness")

        def populate_individual_table():
            self._populate_individual_table(pipeline.data, pipeline.sensitive_attributes, pipeline.performance_results,
                                            pipeline.fairness_results, pipeline.type)

        self.individual_cbMetrics.currentIndexChanged.connect(populate_individual_table)
        self.cbModels.currentIndexChanged.connect(populate_individual_table)

        # add to groupBox
        individualTopLayout.addRow('Model:', self.cbModels)
        individualTopLayout.addRow('Metrics:', self.individual_cbMetrics)

        # add to layout
        self.individual_tab.layout().addWidget(self.individual_metrics_groupBox)
        self._populate_individual_table(pipeline.data, pipeline.sensitive_attributes, pipeline.performance_results,
                                        pipeline.fairness_results, pipeline.type)

    def _populate_individual_table(self, data, sensitive_attributes, performance_results, fairness_results, pl_type):
        self._clear_individual_table()
        # get values from filters
        metric_type = self.individual_cbMetrics.currentText()

        model_idx = self.cbModels.currentIndex()
        models = list(performance_results.keys())
        model = models[model_idx]

        if metric_type == "Performance":
            self.individualPerformanceTable = IndividualPerformanceTable(data, model, performance_results)

            # add to layout
            self.individual_tab.layout().addWidget(self.individualPerformanceTable)
        if metric_type == "Fairness":
            for i, sensitive in enumerate(sensitive_attributes):
                self.sensitiveIndividualTables.append(IndividualFairnessTable(data, model, fairness_results, sensitive,
                                                                              pl_type))

                # add to layout
                self.individual_tab.layout().addWidget(self.sensitiveIndividualTables[i])
            # add removable stretch
            self.stretch_individual = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                            QtWidgets.QSizePolicy.Expanding)
            self.individual_tab.layout().addItem(self.stretch_individual)

    def _clear_individual_table(self):
        try:
            for widget in self.sensitiveIndividualTables:
                widget.setParent(None)
            self.sensitiveIndividualTables = []
            self.individualPerformanceTable.setParent(None)
            self.individual_tab.layout().removeItem(self.stretch_individual)
        except AttributeError:
            return

    def _refresh_tabs(self):
        try:
            self.individual_metrics_groupBox.setParent(None)
            self.overview_metrics_groupBox.setParent(None)
        except AttributeError:
            return

        self._clear_dataset_table()
        self._clear_overview_table()
        self._clear_individual_table()

    def open_individual_tab(self, model_index):
        self.tabs.setCurrentIndex(self.individual_tab_idx)
        self.cbModels.setCurrentIndex(model_index)
