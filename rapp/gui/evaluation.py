# PyQt5
import os.path

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QScrollArea

from rapp.gui.helper import CheckableComboBox
from rapp.gui.widgets import DatasetTables, SummaryTable, InspectionPerformanceTable, InspectionFairnessCollapsible, \
    ParetoCollapsible
from rapp.util import estimator_name
from rapp.fair.metanotion import max_difference


class EvaluationWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(EvaluationWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()

    def initUI(self):
        # create layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(layout)

        # create widgets
        self.tabs = QtWidgets.QTabWidget()

        self.sensitiveDatasetTable = {}
        self.sensitiveInspectionTables = {}
        self.sensitiveParetoTables = {}

        self.cbPerformance = None
        self.cbFairness = None
        self.cbSummaryModes = None
        self.cbSensitiveAttributes = None
        self.summary_groupBox = None

        self.inspection_cbModels = None
        self.inspection_cbMetrics = None
        self.inspectionPerformanceTable = None

        self.__init_dataset_tab()
        self.__init_summary_tab()
        self.__init_inspection_tab()
        self.__init_pareto_tab()

        # add widgets to layout
        layout.addWidget(self.tabs)

    def __init_dataset_tab(self):
        # create layout
        self.dataset_tab = QtWidgets.QWidget()
        self.dataset_tab.setLayout(QtWidgets.QVBoxLayout())
        self.dataset_scroll = QScrollArea()
        self.dataset_scroll.setWidgetResizable(True)
        self.dataset_scroll.setWidget(self.dataset_tab)

        self.dataset_scroll.setStyleSheet("QScrollBar{background-color: white}"
                                             "QWidget#WhiteBackground {background-color: white}")
        self.dataset_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.dataset_tab.setObjectName("WhiteBackground")

        # add to layout
        tab_idx = self.tabs.addTab(self.dataset_scroll, 'Dataset')
        self.dataset_tab_idx = tab_idx

    def __init_summary_tab(self):
        # create layout
        self.summary_tab = QtWidgets.QWidget()
        self.summary_tab.setLayout(QtWidgets.QVBoxLayout())

        # add to layout
        tab_idx = self.tabs.addTab(self.summary_tab, 'Model Summary')
        self.summary_tab_idx = tab_idx

    def __init_inspection_tab(self):
        # create layout
        self.inspection_tab = QtWidgets.QWidget()
        self.inspection_tab.setLayout(QtWidgets.QVBoxLayout())
        self.inspection_scroll = QScrollArea()
        self.inspection_scroll.setWidgetResizable(True)
        self.inspection_scroll.setWidget(self.inspection_tab)

        self.inspection_scroll.setStyleSheet("QScrollBar{background-color: white}"
                                         "QWidget#WhiteBackground {background-color: white}")
        self.inspection_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.inspection_tab.setObjectName("WhiteBackground")

        # add to layout
        tab_idx = self.tabs.addTab(self.inspection_scroll, 'Model Inspection')
        self.inspection_tab_idx = tab_idx

    def __init_pareto_tab(self):
        # create layout
        self.pareto_tab = QtWidgets.QWidget()
        self.pareto_tab.setLayout(QtWidgets.QVBoxLayout())
        self.pareto_scroll = QScrollArea()
        self.pareto_scroll.setWidgetResizable(True)
        self.pareto_scroll.setWidget(self.pareto_tab)

        self.pareto_scroll.setStyleSheet("QScrollBar{background-color: white}"
                                         "QWidget#WhiteBackground {background-color: white}")
        self.pareto_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.pareto_tab.setObjectName("WhiteBackground")

        # add to layout
        tab_idx = self.tabs.addTab(self.pareto_scroll, 'Pareto Front')
        self.pareto_tab_idx = tab_idx

    def populate_tabs(self, pipeline, data_settings):
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
        self._populate_summary_tab(pipeline)
        self._populate_inspection_tab(pipeline)
        self._populate_pareto_tab(pipeline)

    def _populate_dataset_tab(self, data, statistics_results, sensitive_attributes, pl_type, data_settings):
        # one collapsible box per sensitive attribute
        for sensitive in sensitive_attributes:
            self.sensitiveDatasetTable[sensitive] = DatasetTables(sensitive, data,
                                                                  statistics_results, pl_type,
                                                                  data_settings)

            # add to layout
            self.dataset_tab.layout().addWidget(self.sensitiveDatasetTable[sensitive])
        # add removable stretch
        self.stretch_dataset = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)
        self.dataset_tab.layout().addItem(self.stretch_dataset)

    def _clear_dataset_table(self):
        for _, widget in self.sensitiveDatasetTable.items():
            widget.setParent(None)
        self.sensitiveDatasetTable = {}
        self.dataset_tab.layout().removeItem(self.stretch_dataset)

    def _populate_summary_tab(self, pipeline):
        pl_type = pipeline.type.capitalize()
        # comboBox for filtering
        self.cbPerformance = CheckableComboBox()
        self.cbFairness = CheckableComboBox()
        self.cbSummaryModes = QtWidgets.QComboBox()
        self.cbSensitiveAttributes = QtWidgets.QComboBox()

        # groupBox for the filters
        self.summary_metrics_groupBox = QGroupBox("Filters")
        self.summary_metrics_groupBox.size()
        topLayout = QtWidgets.QFormLayout()
        self.summary_metrics_groupBox.setLayout(topLayout)

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
            self.cbSummaryModes.addItem(str(mode).capitalize())

        for sensitive in pipeline.sensitive_attributes:
            self.cbSensitiveAttributes.addItem(str(sensitive).capitalize())

        def populate_summary_table():
            self._populate_summary_table(pipeline.performance_results,
                                         pipeline.fairness_results, pipeline.type)

        self.cbPerformance.currentIndexChanged.connect(populate_summary_table)
        self.cbFairness.currentIndexChanged.connect(populate_summary_table)
        self.cbSummaryModes.currentIndexChanged.connect(populate_summary_table)
        self.cbSensitiveAttributes.currentIndexChanged.connect(populate_summary_table)

        # add to groupBox
        topLayout.addRow(f"{pl_type} Metrics:", self.cbPerformance)
        topLayout.addRow('Fairness Metrics:', self.cbFairness)
        topLayout.addRow('Mode:', self.cbSummaryModes)
        topLayout.addRow('Sensitive Attribute:', self.cbSensitiveAttributes)

        # add to layout
        self.summary_tab.layout().addWidget(self.summary_metrics_groupBox)
        self._populate_summary_table(pipeline.performance_results, pipeline.fairness_results, pipeline.type)

    def _clear_summary_table(self):
        try:
            self.summary_groupBox.setParent(None)
        except AttributeError:
            return

    def _populate_summary_table(self, performance_results, fairness_results, pl_type):
        self._clear_summary_table()
        # get values from filters
        mode = self.cbSummaryModes.currentText().lower()
        sensitive = self.cbSensitiveAttributes.currentText()
        performance_metrics = self.cbPerformance.get_checked_items()
        fairness_notions = self.cbFairness.get_checked_items()
        metrics = self.cbPerformance.get_checked_items()
        metrics.extend(fairness_notions)

        models = list(performance_results.keys())

        # create groupBox
        self.summary_groupBox = SummaryTable(mode, models, metrics, pl_type, performance_metrics,
                                             performance_results, fairness_notions,
                                             fairness_results, sensitive)
        self.summary_groupBox.set_model_click_function(self.open_inspection_tab)

        # add to layout
        self.summary_tab.layout().addWidget(self.summary_groupBox)

    def _populate_inspection_tab(self, pipeline):
        # comboBox for filtering
        self.inspection_cbModels = QtWidgets.QComboBox()
        self.inspection_cbMetrics = QtWidgets.QComboBox()

        # groupBox for the filters
        self.inspection_metrics_groupBox = QGroupBox("Filters")
        topLayout = QtWidgets.QFormLayout()
        self.inspection_metrics_groupBox.setLayout(topLayout)
        self.inspection_metrics_groupBox.setAlignment(Qt.AlignTop)

        # load comboBoxes
        for model in pipeline.performance_results:
            self.inspection_cbModels.addItem(estimator_name(model))
        self.inspection_cbMetrics.addItem("Performance")
        self.inspection_cbMetrics.addItem("Fairness")

        def populate_inspection_table():
            self._populate_inspection_table(pipeline.data, pipeline.sensitive_attributes, pipeline.performance_results,
                                            pipeline.fairness_results, pipeline.type)

        self.inspection_cbMetrics.currentIndexChanged.connect(populate_inspection_table)
        self.inspection_cbModels.currentIndexChanged.connect(populate_inspection_table)

        # add to groupBox
        topLayout.addRow('Model:', self.inspection_cbModels)
        topLayout.addRow('Metrics:', self.inspection_cbMetrics)

        # add to layout
        self.inspection_tab.layout().addWidget(self.inspection_metrics_groupBox)
        self._populate_inspection_table(pipeline.data, pipeline.sensitive_attributes, pipeline.performance_results,
                                        pipeline.fairness_results, pipeline.type)

    def _populate_inspection_table(self, data, sensitive_attributes, performance_results, fairness_results, pl_type):
        self._clear_inspection_table()
        # get values from filters
        metric_type = self.inspection_cbMetrics.currentText()

        model_idx = self.inspection_cbModels.currentIndex()
        models = list(performance_results.keys())
        model = models[model_idx]

        if metric_type == "Performance":
            self.inspectionPerformanceTable = InspectionPerformanceTable(data, model, performance_results)

            # add to layout
            self.inspection_tab.layout().addWidget(self.inspectionPerformanceTable)

        if metric_type == "Fairness":
            for sensitive in sensitive_attributes:
                self.sensitiveInspectionTables[sensitive] = InspectionFairnessCollapsible(data, model, fairness_results,
                                                                                          sensitive,
                                                                                          pl_type)

                # add to layout
                self.inspection_tab.layout().addWidget(self.sensitiveInspectionTables[sensitive])
            # add removable stretch
            self.stretch_inspection = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                            QtWidgets.QSizePolicy.Expanding)
            self.inspection_tab.layout().addItem(self.stretch_inspection)

    def _clear_inspection_table(self):
        try:
            for _, widget in self.sensitiveInspectionTables.items():
                widget.setParent(None)
            self.sensitiveInspectionTables = {}
            self.inspectionPerformanceTable.setParent(None)
            self.inspection_tab.layout().removeItem(self.stretch_inspection)
        except AttributeError:
            return

    def _populate_pareto_tab(self, pipeline):
        pl_type = pipeline.type.capitalize()
        # comboBox for filtering
        self.pareto_cbNotions = QtWidgets.QComboBox()
        self.pareto_cbMetrics = QtWidgets.QComboBox()

        # groupBox for the filters
        self.pareto_metrics_groupBox = QGroupBox("Filters")
        paretoTopLayout = QtWidgets.QFormLayout()
        self.pareto_metrics_groupBox.setLayout(paretoTopLayout)
        self.pareto_metrics_groupBox.setAlignment(Qt.AlignTop)

        # load comboBoxes
        for metric in pipeline.score_functions:
            self.pareto_cbMetrics.addItem(str(metric))
        self.pareto_cbMetrics.setCurrentText('Balanced Accuracy')

        for notion in pipeline.fairness_functions:
            self.pareto_cbNotions.addItem(str(notion))

        # export button
        self.plot_export_button = QtWidgets.QPushButton('Save Plots')
        self.plot_export_button.clicked.connect(self._showExportPlotsDialog)
        self.plot_export_button.setStatusTip('Save pareto plots as PDF file')

        def populate_pareto_table():
            self._populate_pareto_table(pipeline.data, pipeline.sensitive_attributes,
                                        pipeline.performance_results, pipeline.fairness_results, pl_type)

        self.pareto_cbMetrics.currentIndexChanged.connect(populate_pareto_table)
        self.pareto_cbNotions.currentIndexChanged.connect(populate_pareto_table)

        # add to groupBox
        paretoTopLayout.addRow(f'{pl_type} Metric:', self.pareto_cbMetrics)
        paretoTopLayout.addRow('Fairness Notion:', self.pareto_cbNotions)
        paretoTopLayout.addRow('', self.plot_export_button)

        # add to layout
        self.pareto_tab.layout().addWidget(self.pareto_metrics_groupBox)
        populate_pareto_table()

    def _populate_pareto_table(self, data, sensitive_attributes, performance_results, fairness_results, pl_type):
        self._clear_pareto_table()
        # get values from filters
        notion = self.pareto_cbNotions.currentText()
        metric = self.pareto_cbMetrics.currentText()

        models = list(performance_results.keys())
        costs_per_mode = {}

        # Pareto collapsible for eac sensitive attribute
        for sensitive in sensitive_attributes:
            for mode in data:
                costs = np.zeros((len(models), 2))

                for i, model in enumerate(models):
                    notions = fairness_results[model][sensitive][notion]

                    if pl_type == 'Classification':
                        fairness_subgroups = []

                        # The fairness metric returns a dictionary
                        if isinstance(notions[mode], dict):
                            # Get max difference between subgroups
                            for subgroup in notions[mode]:
                                fairness_subgroups.append(notions[mode][subgroup]['affected_percent'])
                            fairness = max_difference(fairness_subgroups)
                            x_label = f"Max Difference {notion}"

                        # The fairness metric returns a single value
                        elif isinstance(notions[mode], np.float64):
                            fairness = notions[mode]
                            x_label = notion

                        performance = performance_results[model][mode]['scores'][metric]
                        y_label = metric
                    if pl_type == 'Regression':
                        fairness = notions[mode]
                        performance = -performance_results[model][mode]['scores'][metric]
                        x_label = notion
                        y_label = f"- {metric}"

                    costs[i] = (fairness, performance)

                costs_per_mode[mode] = costs

            self.sensitiveParetoTables[sensitive] = ParetoCollapsible(data, sensitive, models, costs_per_mode,
                                                                      x_label=x_label, y_label=y_label)

            # add to layout
            self.pareto_tab.layout().addWidget(self.sensitiveParetoTables[sensitive])

        # add removable stretch
        self.stretch_pareto = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                        QtWidgets.QSizePolicy.Expanding)
        self.pareto_tab.layout().addItem(self.stretch_pareto)

    def _clear_pareto_table(self):
        try:
            for _, widget in self.sensitiveParetoTables.items():
                for _, figure in widget.pareto_groupBox.items():
                    figure.close()
                widget.setParent(None)
            self.sensitiveParetoTables = {}
            self.pareto_tab.layout().removeItem(self.stretch_pareto)
        except AttributeError:
            return

    def _refresh_tabs(self):
        try:
            self.inspection_metrics_groupBox.setParent(None)
            self.pareto_metrics_groupBox.setParent(None)
            self.summary_metrics_groupBox.setParent(None)
        except AttributeError:
            return

        self._clear_dataset_table()
        self._clear_summary_table()
        self._clear_inspection_table()
        self._clear_pareto_table()

    def _showExportPlotsDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        dirName = QtWidgets.QFileDialog.getExistingDirectory(self, "Export to folder", "",
                                                             QtWidgets.QFileDialog.ShowDirsOnly)
        if dirName:
            self._export_pareto_plots(dirName)

    def _export_pareto_plots(self, dirName):
        for sensitive, collapsible in self.sensitiveParetoTables.items():
            for mode, plot in collapsible.pareto_groupBox.items():
                if mode == "train":
                    mode = "training"

                file_name = f"pareto_plot_{mode.lower()}_{sensitive.lower()}.pdf"
                file_path = os.path.join(dirName, file_name)

                plot.figure.suptitle(f'{sensitive} - {mode.capitalize()} Set', y=1)
                size = plot.figure.get_size_inches() #* plot.figure.dpi
                plot.figure.set_size_inches(5, 3.5)
                plot.figure.savefig(file_path, bbox_inches="tight")
                plot.figure.set_size_inches(size) # return back to original size after exporting plot

    def open_inspection_tab(self, model_index):
        self.tabs.setCurrentIndex(self.inspection_tab_idx)
        self.inspection_cbModels.setCurrentIndex(model_index)
