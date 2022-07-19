import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from rapp.gui.helper import ClickableLabel, CollapsibleBox
from rapp.util import estimator_name, pareto_front


class DatasetTables(CollapsibleBox):
    def __init__(self, sensitive_attribute, data, statistics_results, pl_type='classification', data_settings=None):
        """
        Generates a collapsible box with the statistics result values, for a specific sensitive attribute, for each mode

        Parameters
        ----------
        sensitive_attribute: str
            Sensitive attribute to use.

        data: rapp.pipeline.data object
            Data used in the pipeline object (used to extract the modes).

        statistics_results: dict
            Statistic results with the form of: rapp.pipeline.statistics_results

        pl_type: {'classification', 'regression}, default : 'classification'
            Which type of prediction task is tackled by the pipeline.

        data_settings: dict (optional), default: None
            It represents the loaded data in the pipeline, it has the form:
                        {'studies_id': studies_id of train data,
                        'features_id': features_id of train data,
                        'labels_id': predicting label_id of the model}
        """
        super(DatasetTables, self).__init__(sensitive_attribute.capitalize())

        self.statistics_results = statistics_results

        if data_settings is not None:
            labels_id = data_settings.get("labels_id")

        self.sensitiveHBoxLayout = QtWidgets.QHBoxLayout()
        self.main_groupBox = {}
        self.dataset_groupBox = {}

        for mode in data:
            self.main_groupBox[mode] = (QtWidgets.QGroupBox(mode.capitalize()))
            hBoxLayout = QtWidgets.QHBoxLayout()
            self.main_groupBox[mode].setLayout(hBoxLayout)

            if pl_type == "classification":
                self.dataset_groupBox[mode] = DatasetTable(statistics_results, mode, sensitive_attribute)

            if pl_type == "regression":
                self.dataset_groupBox[mode] = DatasetPlot(statistics_results, mode, sensitive_attribute, labels_id)

            hBoxLayout.addWidget(self.dataset_groupBox[mode])
            self.sensitiveHBoxLayout.addWidget(self.main_groupBox[mode])
        self.setContentLayout(self.sensitiveHBoxLayout)


class DatasetTable(QtWidgets.QGroupBox):
    def __init__(self, statistics_results, mode, sensitive_attribute):
        """
        Generates a table with the given metrics

        Parameters
        ----------
        statistics_results: dict
            Statistic results with the form of: rapp.pipeline.statistics_results

        mode: {'train', 'test'}
            Which mode should be accessed.

        sensitive_attribute: str (optional)
            Sensitive attribute to use, only needed if fairness results.
        """
        super(DatasetTable, self).__init__()

        self.setFlat(True)
        self.setStyleSheet("border:0;")
        tableGridLayout = QtWidgets.QGridLayout()
        self.setLayout(tableGridLayout)
        self.labels = {}

        subgroups = list(statistics_results[mode]['groups'][sensitive_attribute].keys())
        classes = list(statistics_results[mode]['outcomes'].keys())

        # 'Class' label
        labelClass = QtWidgets.QLabel()
        labelClass.setText("Class")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 0, 0)
        self.labels[labelClass] = []

        # 'Total' label
        labelClassTotal = QtWidgets.QLabel()
        labelClassTotal.setText("Total")
        labelClassTotal.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClassTotal, 0, len(subgroups) + 1)
        self.labels[labelClassTotal] = []

        for i, subgroup in enumerate(subgroups):
            # subgroups labels
            labelSubgroup = QtWidgets.QLabel()
            labelSubgroup.setText(str(subgroup).capitalize())
            labelSubgroup.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelSubgroup, 0, i + 1)
            self.labels[labelSubgroup] = []

            for j, class_name in enumerate(classes):
                # classes labels
                if i == 0:
                    labelClasses = QtWidgets.QLabel()
                    labelClasses.setText(str(class_name).capitalize())
                    labelClasses.setStyleSheet("font-weight: bold")
                    tableGridLayout.addWidget(labelClasses, j + 1, 0)
                    self.labels[labelClass].append(labelClasses)

                    # class total value labels
                    total_class = statistics_results[mode]['outcomes'][class_name]
                    labelClassTotalValues = QtWidgets.QLabel()
                    labelClassTotalValues.setText(str(total_class))
                    tableGridLayout.addWidget(labelClassTotalValues, j + 1, len(subgroups) + 1)
                    self.labels[labelClassTotal].append(labelClassTotalValues)

                # value labels
                value = statistics_results[mode]['groups'][sensitive_attribute][subgroup]['outcomes'][
                    class_name]
                labelValue = QtWidgets.QLabel()
                labelValue.setText(str(value))
                tableGridLayout.addWidget(labelValue, j + 1, i + 1)
                self.labels[labelSubgroup].append(labelValue)

            # subgroups total value labels
            total_subgroup = statistics_results[mode]['groups'][sensitive_attribute][subgroup]['total']
            labelSubgroupTotalValue = QtWidgets.QLabel()
            labelSubgroupTotalValue.setText(str(total_subgroup))
            tableGridLayout.addWidget(labelSubgroupTotalValue, len(classes) + 1, i + 1)
            self.labels[labelSubgroup].append(labelSubgroupTotalValue)

        # total outcomes value label
        total_samples = statistics_results[mode]['total']
        labelTotalSamplesValue = QtWidgets.QLabel()
        labelTotalSamplesValue.setText(str(total_samples))
        tableGridLayout.addWidget(labelTotalSamplesValue, len(classes) + 1, len(subgroups) + 1)
        self.labels[labelClassTotal].append(labelTotalSamplesValue)

        # 'Total' label
        labelSubgroupTotal = QtWidgets.QLabel()
        labelSubgroupTotal.setText("Total")
        labelSubgroupTotal.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelSubgroupTotal, len(classes) + 1, 0)
        self.labels[labelClass].append(labelSubgroupTotal)


class DatasetPlot(QtWidgets.QGroupBox):
    def __init__(self, statistics_results, mode, sensitive_attribute, labels_id):
        """
        Generates a table with the given metrics

        Parameters
        ----------
        statistics_results: dict
            Statistic results with the form of: rapp.pipeline.statistics_results

        mode: {'train', 'test'}
            Which mode should be accessed.

        sensitive_attribute: str (optional)
            Sensitive attribute to use, only needed if fairness results.
        """
        super(DatasetPlot, self).__init__()

        self.setFlat(True)
        self.setStyleSheet("border:0;")
        vBoxLayout = QtWidgets.QVBoxLayout()
        self.setLayout(vBoxLayout)
        self.setMinimumHeight(200)

        # add fig canvas to groupBox
        fig, ax = plt.subplots(figsize=(5, 3))
        plotCanvas = FigureCanvas(fig)
        vBoxLayout.addWidget(plotCanvas, alignment=Qt.AlignCenter)

        self.figure = fig

        # plot subgroups outcomes
        subgroups = list(statistics_results[mode]['groups'][sensitive_attribute].keys())
        for k, subgroup in enumerate(subgroups):
            outcomes = statistics_results[mode]['groups'][sensitive_attribute][subgroup]['outcomes']
            ax.hist(outcomes, label=str(subgroup), density=True, histtype="step")

            plt.legend()
            plt.xlabel(labels_id)
            plt.ylabel('Density')
            fig.tight_layout()

        plotCanvas.draw()


class OverviewTable(QtWidgets.QGroupBox):
    def __init__(self, mode, models, metrics, pl_type, performance_metrics, performance_results, fairness_notions=None,
                 fairness_results=None, sensitive_attribute=None):
        """
        Generates a table with the performance and fairness result values, for a specific mode and sensitive attribute,
        for each model.

        Parameters
        ----------
        mode: str
            Mode to use.

        models: list
            List of Scikit-learn estimators.

        metrics: list
            List of metrics to be added to the table.

        pl_type: {'classification', 'regression}
            Which type of prediction task is tackled by the pipeline.

        performance_metrics: list
            List of performance metrics to generate in the table.

        performance_results: dict
            Performance results with the form of: rapp.pipeline.performance_results.

        fairness_notions: list (optional)
            List of fairness notions to generate in the table.

        fairness_results: dict (optional)
            Fairness results with the form of: rapp.pipeline.fairness_results.

        sensitive_attribute: str (optional)
            Sensitive attribute to use, only needed if fairness results.

        """

        if sensitive_attribute is not None:
            super(OverviewTable, self).__init__(f"{str(mode).capitalize()} - {sensitive_attribute}:")
        if sensitive_attribute is None:
            super(OverviewTable, self).__init__(f"{str(mode).capitalize()}:")

        self.setFlat(True)
        self.setStyleSheet("border:0;")
        tableGridLayout = QtWidgets.QGridLayout()
        self.setLayout(tableGridLayout)
        self.labels = {}

        labelModel = QtWidgets.QLabel()
        labelModel.setText("Model")
        labelModel.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelModel, 0, 0, Qt.AlignLeft)
        self.labels[labelModel] = []

        # metrics labels
        for i, metric in enumerate(metrics):
            labelMetric = QtWidgets.QLabel()
            labelMetric.setText(str(metric))
            labelMetric.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelMetric, 0, i + 1, Qt.AlignRight)
            self.labels[labelMetric] = []

            # model labels
            for j, model in enumerate(models):
                if i == 0:
                    est_name = estimator_name(model)
                    labelModels = ClickableLabel(j)
                    labelModels.setText(est_name)
                    tableGridLayout.addWidget(labelModels, j + 1, 0, Qt.AlignLeft)
                    self.labels[labelModel].append(labelModels)

                if metric in performance_metrics:
                    # performance metrics
                    value = performance_results[model][mode]['scores'][metric]
                    labelValue = QtWidgets.QLabel()
                    labelValue.setText(f"{value:.3f}")
                    tableGridLayout.addWidget(labelValue, j + 1, i + 1, Qt.AlignRight)
                    self.labels[labelMetric].append(labelValue)

                if metric in fairness_notions:
                    # fairness notions
                    values = fairness_results[model][sensitive_attribute][metric][mode]
                    if pl_type == "classification":
                        # average value across sensitive attribute
                        measure = np.zeros(len(values))
                        for k, value in enumerate(values):
                            measure[k] = values[value]['affected_percent']

                        measure = np.mean(measure)

                    if pl_type == "regression":
                        measure = values

                    labelValue = QtWidgets.QLabel()
                    labelValue.setText(f"{measure:.3f}")
                    tableGridLayout.addWidget(labelValue, j + 1, i + 1, Qt.AlignRight)
                    self.labels[labelMetric].append(labelValue)

    def set_model_click_function(self, function):
        key = list(self.labels.keys())[0]
        for labelModel in self.labels[key]:
            labelModel.set_click_function(function)


class IndividualPerformanceTable(QtWidgets.QGroupBox):
    def __init__(self, data, model, performance_results):
        """
        Generates a table with the performance and fairness result values, for a specific mode and sensitive attribute,
        for a specific model.

        Parameters
        ----------
        data: rapp.pipeline.data object
            Data used in the pipeline object (used to extract the modes)

        model: Scikit-learn estimator
            Selected individual estimator.

        performance_results: dict
            Performance results with the form of: rapp.pipeline.performance_results.

        """

        super(IndividualPerformanceTable, self).__init__()

        HBoxLayout = QtWidgets.QHBoxLayout()
        self.setLayout(HBoxLayout)
        self.setObjectName("NoBorderGroupBox")
        self.setStyleSheet("QGroupBox#NoBorderGroupBox {border:0;padding.top: 11;}")

        self.cm_groupBox = {}
        self.metrics_groupBox = {}
        self.main_groupBox = {}

        for mode in data:
            # main_groupBox for each mode
            self.main_groupBox[mode] = QtWidgets.QGroupBox(mode.capitalize())
            vBoxLayout = QtWidgets.QVBoxLayout()
            self.main_groupBox[mode].setLayout(vBoxLayout)
            self.main_groupBox[mode].setObjectName("NoBorderGroupBox")

            confusion_matrix = performance_results[model][mode]['confusion_matrix']
            if len(confusion_matrix) > 0:
                # groupBox for confusion Matrix
                self.cm_groupBox[mode] = ConfusionMatrixTable(confusion_matrix)
                # individual_cm_groupBox[i].setMinimumHeight(200)

            metrics = performance_results[model][mode]['scores']
            # groupBox for metrics
            self.metrics_groupBox[mode] = PerformanceMetricsTable(metrics)
            # individual_metrics_groupBox[i].setMinimumHeight(200)

            # add to layout
            if len(self.cm_groupBox) > 0:
                vBoxLayout.addWidget(self.cm_groupBox[mode])
            vBoxLayout.addWidget(self.metrics_groupBox[mode])
            vBoxLayout.addStretch()
            HBoxLayout.addWidget(self.main_groupBox[mode])


class ConfusionMatrixTable(QtWidgets.QGroupBox):
    def __init__(self, confusion_matrix):
        """
        Generates a table with the confusion matrix

        Parameters
        ----------
        confusion_matrix: np.array with the shape of (n_classes, n_classes)

        """
        super(ConfusionMatrixTable, self).__init__()

        tableGridLayout = QtWidgets.QGridLayout()
        self.setLayout(tableGridLayout)
        self.labels = {}

        # headers labels
        labelClass = QtWidgets.QLabel()
        labelClass.setText("Class")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 1, 1, alignment=Qt.AlignRight)
        self.labels[labelClass] = []

        labelTitle = QtWidgets.QLabel()
        labelTitle.setText("Predicted as")
        labelTitle.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelTitle, 0, 1 + len(confusion_matrix) / 2, 1, len(confusion_matrix),
                                  alignment=Qt.AlignCenter)
        self.title = labelTitle

        # labelClass = QtWidgets.QLabel()
        # labelClass.setText("Actual")
        # labelClass.setStyleSheet("font-weight: bold")
        # tableGridLayout.addWidget(labelClass, 1 + len(confusion_matrix) / 2, 0, alignment=Qt.AlignCenter)

        for j in range(len(confusion_matrix)):
            # class labels
            labelClassPred = QtWidgets.QLabel()
            labelClassPred.setText(str(j))
            labelClassPred.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelClassPred, 1, j + 2, alignment=Qt.AlignRight)
            self.labels[labelClassPred] = []

            labelClassTrue = QtWidgets.QLabel()
            labelClassTrue.setText(str(j))
            tableGridLayout.addWidget(labelClassTrue, j + 2, 1, alignment=Qt.AlignRight)
            self.labels[labelClass].append(labelClassTrue)

            for k, cm in enumerate(confusion_matrix):
                # values
                value = cm[j]
                labelValue = QtWidgets.QLabel()
                labelValue.setText(str(value))
                tableGridLayout.addWidget(labelValue, k + 2, j + 2, alignment=Qt.AlignRight)
                self.labels[labelClassPred].append(labelValue)


class PerformanceMetricsTable(QtWidgets.QGroupBox):
    def __init__(self, metrics):
        """
        Generates a table with the given metrics

        Parameters
        ----------
        metrics: dict[metric -> value]
        """
        super(PerformanceMetricsTable, self).__init__()

        tableGridLayout = QtWidgets.QGridLayout()
        self.setLayout(tableGridLayout)
        self.labels = {}

        labelMetric = QtWidgets.QLabel()
        labelMetric.setText("Metric")
        labelMetric.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelMetric, 0, 0, alignment=Qt.AlignLeft)
        self.labels[labelMetric] = []

        labelValue = QtWidgets.QLabel()
        labelValue.setText("Value")
        labelValue.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelValue, 0, 1, alignment=Qt.AlignRight)
        self.labels[labelValue] = []

        for j, metric in enumerate(metrics):
            # performance metrics labels
            labelMetrics = QtWidgets.QLabel()
            labelMetrics.setText(str(metric).capitalize())
            tableGridLayout.addWidget(labelMetrics, j + 1, 0, alignment=Qt.AlignLeft)
            self.labels[labelMetric].append(labelMetrics)
            # performance measures
            value = metrics[metric]
            labelValues = QtWidgets.QLabel()
            labelValues.setText(f"{value:.3f}")
            tableGridLayout.addWidget(labelValues, j + 1, 1, alignment=Qt.AlignRight)
            self.labels[labelValue].append(labelValues)


class IndividualFairnessTable(CollapsibleBox):
    def __init__(self, data, model, fairness_results, sensitive_attribute, pl_type='classification'):
        """
        Generates a collapsible box with the performance and fairness result values, for a specific mode and sensitive attribute,
        for each model.

        Parameters
        ----------
        data: rapp.pipeline.data object
            Data used in the pipeline object (used to extract the modes)

        model: Scikit-learn estimator
            Selected individual estimator.

        fairness_results: dict
            Performance results with the form of: rapp.pipeline.performance_results.

        sensitive_attribute: str (optional)
            Sensitive attribute to use, only needed if fairness results.

        pl_type: {'classification', 'regression}, default : 'classification'
            Which type of prediction task is tackled by the pipeline.
        """

        super(IndividualFairnessTable, self).__init__(sensitive_attribute.capitalize())

        HBoxLayout = QtWidgets.QHBoxLayout()

        self.ct_groupBox = {}
        self.metrics_groupBox = {}
        self.main_groupBox = {}

        # groupBox for each mode
        for i, mode in enumerate(data):
            self.main_groupBox[mode] = QtWidgets.QGroupBox(mode.capitalize())
            vBoxLayout = QtWidgets.QVBoxLayout()
            self.main_groupBox[mode].setFlat(True)
            self.main_groupBox[mode].setLayout(vBoxLayout)
            self.main_groupBox[mode].setStyleSheet("QGroupBox#NoBorderGroupBox {border:0; padding.top: 8;}")
            self.main_groupBox[mode].setObjectName("NoBorderGroupBox")

            # correspondence table
            if pl_type == "classification":
                # Since the confusion matrix is the same for all metrics we are going to access the first cm that appears
                first_metric = list(fairness_results[model][sensitive_attribute].keys())[0]
                sub_groups = fairness_results[model][sensitive_attribute][first_metric][mode]
                self.ct_groupBox[mode] = CorrespondenceTable(sub_groups)

            # metrics table
            metrics = fairness_results[model][sensitive_attribute]
            self.metrics_groupBox[mode] = FairnessMetricsTable(metrics, mode, pl_type)

            # add to layout
            if len(self.ct_groupBox) > 0:
                vBoxLayout.addWidget(self.ct_groupBox[mode])
            vBoxLayout.addWidget(self.metrics_groupBox[mode])
            vBoxLayout.addStretch()
            HBoxLayout.addWidget(self.main_groupBox[mode])

        self.setContentLayout(HBoxLayout)


class CorrespondenceTable(QtWidgets.QGroupBox):
    def __init__(self, sub_groups):
        """
        Generates a table with the confusion matrix

        Parameters
        ----------
        sub_groups: dict[sub_group -> confusion_matrix]
            Dictionary where 'confusion_matrix' is used as a key to access the sub_group's confusion_matrix
        """
        super(CorrespondenceTable, self).__init__()

        # groupBox for correspondence table
        tableGridLayout = QtWidgets.QGridLayout()
        self.setLayout(tableGridLayout)
        self.labels = {}

        # 'Class' label
        labelClass = QtWidgets.QLabel()
        labelClass.setText("Class")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 0, 0, alignment=Qt.AlignLeft)
        self.labels[labelClass] = []

        for j, sub_group in enumerate(sub_groups):
            # subgroup labels
            labelSubgroup = QtWidgets.QLabel()
            labelSubgroup.setText(str(sub_group).capitalize())
            labelSubgroup.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelSubgroup, 0, j + 1, alignment=Qt.AlignRight)
            self.labels[labelSubgroup] = []

            confusion_matrix = sub_groups[sub_group]['confusion_matrix']
            n = int(np.sqrt(len(confusion_matrix)))
            cm = np.array(confusion_matrix).reshape(n, n)

            values = np.sum(cm, axis=0)
            for k, total in enumerate(values):
                # values labels
                labelValue = QtWidgets.QLabel()
                labelValue.setText(str(total))
                tableGridLayout.addWidget(labelValue, k + 1, j + 1, alignment=Qt.AlignRight)
                self.labels[labelSubgroup].append(labelValue)

        for i in range(len(cm)):
            # classes labels
            labelClasses = QtWidgets.QLabel()
            labelClasses.setText(str(i))
            tableGridLayout.addWidget(labelClasses, i + 1, 0, alignment=Qt.AlignLeft)
            self.labels[labelClass].append(labelClasses)


class FairnessMetricsTable(QtWidgets.QGroupBox):
    def __init__(self, metrics, mode, pl_type):
        """
        Generates a table with the given metrics

        Parameters
        ----------
        metrics: dict[metric -> value]

        mode: {'train', 'test'}
            Which mode should be accessed.

        pl_type: {'classification', 'regression}
            Which type of prediction task is tackled by the pipeline.
        """
        super(FairnessMetricsTable, self).__init__()

        tableGridLayout = QtWidgets.QGridLayout()
        self.setLayout(tableGridLayout)
        self.labels = {}

        # 'metric' label
        labelMetric = QtWidgets.QLabel()
        labelMetric.setText("Metric")
        labelMetric.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelMetric, 0, 0, alignment=Qt.AlignLeft)
        self.labels[labelMetric] = []

        if pl_type == "regression":
            # 'value' labels
            labelValue = QtWidgets.QLabel()
            labelValue.setText("Value")
            labelValue.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelValue, 0, 1, alignment=Qt.AlignRight)
            self.labels[labelValue] = []

            for j, metric in enumerate(metrics):
                # fairness metrics labels
                labelMetrics = QtWidgets.QLabel()
                labelMetrics.setText(str(metric).capitalize())
                tableGridLayout.addWidget(labelMetrics, j + 1, 0, alignment=Qt.AlignLeft)
                self.labels[labelMetric].append(labelMetrics)

                values = metrics[metric][mode]
                # fairness measures
                labelValues = QtWidgets.QLabel()
                labelValues.setText(f"{values:.3f}")
                tableGridLayout.addWidget(labelValues, j + 1, 1, alignment=Qt.AlignRight)
                self.labels[labelValue].append(labelValues)

        if pl_type == "classification":
            first_metric = list(metrics.keys())[0]
            for i, subgroup in enumerate(metrics[first_metric][mode]):
                # subgroup labels
                labelSubgroup = QtWidgets.QLabel()
                labelSubgroup.setText(str(subgroup).capitalize())
                tableGridLayout.addWidget(labelSubgroup, 0, i + 1, alignment=Qt.AlignRight)
                self.labels[labelSubgroup] = []

                for j, metric in enumerate(metrics):

                    if i == 0:
                        # fairness metrics labels
                        labelMetrics = QtWidgets.QLabel()
                        labelMetrics.setText(str(metric).capitalize())
                        tableGridLayout.addWidget(labelMetrics, j + 1, 0, alignment=Qt.AlignLeft)
                        self.labels[labelMetric].append(labelMetrics)

                    measure = metrics[metric][mode][subgroup]['affected_percent']
                    # fairness measures
                    labelValues = QtWidgets.QLabel()
                    labelValues.setText(f"{measure:.3f}")
                    tableGridLayout.addWidget(labelValues, j + 1, i + 1, alignment=Qt.AlignRight)
                    self.labels[labelSubgroup].append(labelValues)


class ParetoCollapsible(CollapsibleBox):
    def __init__(self, data, sensitive_attribute, models, costs, x_label, y_label):
        """
        Generates a collapsible box with the statistics result values, for a specific sensitive attribute, for each mode

        Parameters
        ----------
        data: rapp.pipeline.data object
            Data used in the pipeline object (used to extract the modes)

        sensitive_attribute: str
            Sensitive attribute to use.

        models: list
            List of Scikit-learn estimators.

        costs: dict {mode -> np.array (n_samples, n_costs)}
            Costs from which to extract the pareto optimal indices.
        """
        super(ParetoCollapsible, self).__init__(sensitive_attribute.capitalize())

        self.sensitiveHBoxLayout = QtWidgets.QHBoxLayout()
        self.main_groupBox = {}
        self.pareto_groupBox = {}

        model_names = [estimator_name(model) for model in models]

        for mode in data:
            self.main_groupBox[mode] = (QtWidgets.QGroupBox(mode.capitalize()))
            hBoxLayout = QtWidgets.QHBoxLayout()
            self.main_groupBox[mode].setLayout(hBoxLayout)

            self.pareto_groupBox[mode] = ParetoPlot(model_names, costs[mode], x_label=x_label, y_label=y_label)

            hBoxLayout.addWidget(self.pareto_groupBox[mode])
            self.sensitiveHBoxLayout.addWidget(self.main_groupBox[mode])

        self.setContentLayout(self.sensitiveHBoxLayout)


class ParetoPlot(QtWidgets.QGroupBox):
    def __init__(self, legend, costs, x_label, y_label):
        """
        Generates a pareto plot with the given costs.

        Parameters
        ----------
        legend: list
            List of values for the legend.

        costs: np.array (n_samples, n_costs)
            Costs from which to extract the pareto optimal indices.

        x_label: str
            Label for the X-axis.

        y_label: str
            Label for the Y-axis.
        """
        super(ParetoPlot, self).__init__()

        self.setFlat(True)
        self.setStyleSheet("border:0;")
        vBoxLayout = QtWidgets.QVBoxLayout()
        self.setLayout(vBoxLayout)
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        self.costs = costs

        # add fig canvas to groupBox
        fig, ax = plt.subplots(figsize=(6, 4))
        plotCanvas = FigureCanvas(fig)
        vBoxLayout.addWidget(plotCanvas, alignment=Qt.AlignCenter)

        self.figure = fig

        # we want to minimize the unfairness and maximize performance
        pareto_costs = self.costs * (-1, 1)
        front = pareto_front(pareto_costs)

        # plot each model's pareto front
        for i, model in enumerate(legend):
            if front[i]:
                color = 'r'
            else:
                color = 'b'
            ax.scatter(self.costs[i, 0], self.costs[i, 1], label=model, c=color)

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        fig.tight_layout()

        plotCanvas.draw()

    def close_fig(self):
        self.fig.close()
