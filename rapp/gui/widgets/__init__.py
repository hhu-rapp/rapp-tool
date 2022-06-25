import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from rapp.gui.helper import ClickableLabel
from rapp.util import estimator_name


class DatasetTable(QtWidgets.QGroupBox):
    def __init__(self, sensitive_attribute, data, statistics_results, data_settings=None):
        """
        Generates a table with the statistics result values, for a specific sensitive attribute, for each mode

        Parameters
        ----------
        sensitive_attribute: str
            Sensitive attribute to use.

        data: rapp.pipeline.data object
            Data used in the pipeline object (used to extract the modes).

        statistics_results: dict
            Statistic results with the form of: rapp.pipeline.statistics_results

        data_settings: dict (optional), default: None
            It represents the loaded data in the pipeline, it has the form:
                        {'studies_id': studies_id of train data,
                        'features_id': features_id of train data,
                        'labels_id': predicting label_id of the model}
        """
        super(DatasetTable, self).__init__()

        self.sensitive = sensitive_attribute
        self.data = data
        self.statistics_results = statistics_results
        self.labels_id = data_settings.get("labes_id", None)

        self.sensitiveHBoxLayout = QtWidgets.QHBoxLayout()
        self.setTitle(sensitive_attribute.capitalize())
        self.setLayout(self.sensitiveHBoxLayout)

    def populate_table(self):
        # TODO Upgrade groupBox to collapsible section
        # one groupBox per mode
        groupbox = []
        for j, mode in enumerate(self.data):
            groupbox.append(QtWidgets.QGroupBox(mode.capitalize()))
            tableGridLayout = QtWidgets.QGridLayout()
            groupbox[j].setLayout(tableGridLayout)

            # 'Class' label
            labelClass = QtWidgets.QLabel()
            labelClass.setText("Class")
            labelClass.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelClass, 0, 0)

            # subgroups labels
            subgroups = list(self.statistics_results[mode]['groups'][self.sensitive].keys())
            for k, subgroup in enumerate(subgroups):
                labelSubgroup = QtWidgets.QLabel()
                labelSubgroup.setText(str(subgroup).capitalize())
                labelSubgroup.setStyleSheet("font-weight: bold")
                tableGridLayout.addWidget(labelSubgroup, 0, k + 1)

                # classes labels
                classes = list(self.statistics_results[mode]['outcomes'].keys())
                for l, class_name in enumerate(classes):
                    labelClass = QtWidgets.QLabel()
                    labelClass.setText(str(class_name).capitalize())
                    labelClass.setStyleSheet("font-weight: bold")
                    tableGridLayout.addWidget(labelClass, l + 1, 0)

                    # value labels
                    value = self.statistics_results[mode]['groups'][self.sensitive][subgroup]['outcomes'][
                        class_name]
                    labelValue = QtWidgets.QLabel()
                    labelValue.setText(str(value))
                    tableGridLayout.addWidget(labelValue, l + 1, k + 1)

                    # class total labels
                    total_class = self.statistics_results[mode]['outcomes'][class_name]
                    labelClasstotal = QtWidgets.QLabel()
                    labelClasstotal.setText(str(total_class))
                    tableGridLayout.addWidget(labelClasstotal, l + 1, len(subgroups) + 1)

                # subgroups total labels
                total_subgroup = self.statistics_results[mode]['groups'][self.sensitive][subgroup]['total']
                labelSubtotal = QtWidgets.QLabel()
                labelSubtotal.setText(str(total_subgroup))
                tableGridLayout.addWidget(labelSubtotal, len(classes) + 1, k + 1)

            # total labels
            labelTotal = QtWidgets.QLabel()
            labelTotal.setText("Total")
            labelTotal.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelTotal, 0, len(subgroups) + 1)

            labelTotal2 = QtWidgets.QLabel()
            labelTotal2.setText("Total")
            labelTotal2.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelTotal2, len(classes) + 1, 0)

            # total outcomes label
            total_samples = self.statistics_results[mode]['total']
            labelSampleTotal = QtWidgets.QLabel()
            labelSampleTotal.setText(str(total_samples))
            tableGridLayout.addWidget(labelSampleTotal, len(classes) + 1, len(subgroups) + 1)

            self.sensitiveHBoxLayout.addWidget(groupbox[j])

    def populate_plot(self):
        # TODO Upgrade groupBox to collapsible section
        # one groupBox per mode
        groupbox = []
        for j, mode in enumerate(self.data):
            groupbox.append(QtWidgets.QGroupBox(mode.capitalize()))
            vBoxLayout = QtWidgets.QVBoxLayout()
            groupbox[j].setLayout(vBoxLayout)

            # add fig canvas to groupBox
            fig, ax = plt.subplots(figsize=(5, 3))
            plotCanvas = FigureCanvas(fig)
            vBoxLayout.addWidget(plotCanvas, alignment=Qt.AlignCenter)

            # plot subgroups outcomes
            subgroups = list(self.statistics_results[mode]['groups'][self.sensitive].keys())
            for k, subgroup in enumerate(subgroups):
                outcomes = self.statistics_results[mode]['groups'][self.sensitive][subgroup]['outcomes']
                ax.hist(outcomes, label=str(subgroup), density=True, histtype="step")

                plt.legend()
                plt.xlabel(self.labels_id)
                plt.ylabel('Density')
                fig.tight_layout()

            plotCanvas.draw()

            self.sensitiveHBoxLayout.addWidget(groupbox[j])


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
        self.labelModels = []

        # model labels
        for i, model in enumerate(models):
            self.labelModels.append(ClickableLabel(i))
            self.labelModels[i].setText(estimator_name(model))
            self.labelModels[i].setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(self.labelModels[i], i + 1, 0)

            # metrics labels
            for j, metric in enumerate(metrics):
                labelMetric = QtWidgets.QLabel()
                labelMetric.setText(str(metric))
                labelMetric.setStyleSheet("font-weight: bold")
                tableGridLayout.addWidget(labelMetric, 0, j + 1)

                if metric in performance_metrics:
                    # performance metrics
                    value = performance_results[model][mode]['scores'][metric]
                    labelValue = QtWidgets.QLabel()
                    labelValue.setText(f"{value:.3f}")
                    tableGridLayout.addWidget(labelValue, i + 1, j + 1)

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
                    tableGridLayout.addWidget(labelValue, i + 1, j + 1)

    def set_model_click_function(self, function):
        for labelModel in self.labelModels:
            labelModel.set_click_function(function)


class IndividualPerformanceTable(QtWidgets.QGroupBox):
    def __init__(self, data, model, performance_results):
        """
        Generates a table with the performance and fairness result values, for a specific mode and sensitive attribute, 
        for each model.

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

        individual_mode_groupBox = []
        individual_cm_groupBox = []
        individual_metrics_groupBox = []
        for i, mode in enumerate(data):
            # groupBox for each mode
            individual_mode_groupBox.append(QtWidgets.QGroupBox(mode.capitalize()))
            vBoxLayout = QtWidgets.QVBoxLayout()
            individual_mode_groupBox[i].setLayout(vBoxLayout)
            individual_mode_groupBox[i].setObjectName("NoBorderGroupBox")

            confusion_matrix = performance_results[model][mode]['confusion_matrix']
            if len(confusion_matrix) > 0:
                # groupBox for confusion Matrix
                individual_cm_groupBox.append(ConfusionMatrixTable(confusion_matrix))
                individual_cm_groupBox[i].setMinimumHeight(200)

            metrics = performance_results[model][mode]['scores']
            # groupBox for metrics
            individual_metrics_groupBox.append(PerformanceMetricsTable(metrics))
            individual_metrics_groupBox[i].setMinimumHeight(200)

            # add to layout
            if len(individual_cm_groupBox) > 0:
                vBoxLayout.addWidget(individual_cm_groupBox[i])
            vBoxLayout.addWidget(individual_metrics_groupBox[i])
            vBoxLayout.addStretch()
            HBoxLayout.addWidget(individual_mode_groupBox[i])


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

        # headers labels
        labelClass = QtWidgets.QLabel()
        labelClass.setText("Class")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 1, 1, alignment=Qt.AlignCenter)

        labelClass = QtWidgets.QLabel()
        labelClass.setText("Predicted")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 0, 1 + len(confusion_matrix) / 2, alignment=Qt.AlignCenter)

        labelClass = QtWidgets.QLabel()
        labelClass.setText("Actual")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 1 + len(confusion_matrix) / 2, 0, alignment=Qt.AlignCenter)

        for j in range(len(confusion_matrix)):
            for k, value in enumerate(confusion_matrix[j]):
                # class labels
                labelClassPred = QtWidgets.QLabel()
                labelClassPred.setText(str(k))
                labelClassPred.setStyleSheet("font-weight: bold")
                tableGridLayout.addWidget(labelClassPred, 1, k + 2, alignment=Qt.AlignCenter)

                labelClassTrue = QtWidgets.QLabel()
                labelClassTrue.setText(str(k))
                labelClassTrue.setStyleSheet("font-weight: bold")
                tableGridLayout.addWidget(labelClassTrue, k + 2, 1, alignment=Qt.AlignCenter)
                # values
                labelValue = QtWidgets.QLabel()
                labelValue.setText(str(value))
                tableGridLayout.addWidget(labelValue, j + 2, k + 2, alignment=Qt.AlignCenter)


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

        labelMetric = QtWidgets.QLabel()
        labelMetric.setText("Metric")
        labelMetric.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelMetric, 0, 0, alignment=Qt.AlignCenter)

        labelValue = QtWidgets.QLabel()
        labelValue.setText("Value")
        labelValue.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelValue, 0, 1, alignment=Qt.AlignCenter)

        for j, metric in enumerate(metrics):
            # performance metrics labels
            labelMetric = QtWidgets.QLabel()
            labelMetric.setText(str(metric).capitalize())
            labelMetric.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelMetric, j + 1, 0, alignment=Qt.AlignCenter)
            # performance measures
            value = metrics[metric]
            labelValue = QtWidgets.QLabel()
            labelValue.setText(f"{value:.3f}")
            tableGridLayout.addWidget(labelValue, j + 1, 1, alignment=Qt.AlignCenter)


class IndividualFairnessTable(QtWidgets.QGroupBox):
    def __init__(self, data, model, fairness_results, sensitive_attribute, pl_type='classification'):
        """
        Generates a table with the performance and fairness result values, for a specific mode and sensitive attribute, 
        for each model.

        Parameters
        ----------
        data: rapp.pipeline.data object
            Data used in the pipeline object (used to extract the modes)

        model: Scikit-learn estimator
            Selected individual estimator.

        fairness_results: dict
            Performance results with the form of: rapp.pipeline.performance_results.

        sensitive_attribute: list
            Sensitive attributes used in the pipeline.

        pl_type: {'classification', 'regression}, default : 'classification'
            Which type of prediction task is tackled by the pipeline.
        """

        super(IndividualFairnessTable, self).__init__()

        HBoxLayout = QtWidgets.QHBoxLayout()
        self.setLayout(HBoxLayout)
        self.setTitle(sensitive_attribute.capitalize())
        self.setStyleSheet("QGroupBox#NoBorderGroupBox {border:0;padding.top: 11;}")

        individual_mode_groupBox = []
        individual_ct_groupBox = []
        individual_metrics_groupBox = []

        # TODO Upgrade groupBox to collapsible section
        # groupBox for each mode
        for i, mode in enumerate(data):
            individual_mode_groupBox.append(QtWidgets.QGroupBox(mode.capitalize()))
            vBoxLayout = QtWidgets.QVBoxLayout()
            individual_mode_groupBox[i].setLayout(vBoxLayout)
            individual_mode_groupBox[i].setObjectName("NoBorderGroupBox")

            # correspondence table
            if pl_type == "classification":
                # Since the confusion matrix is the same for all metrics we are going to access the first cm that appears
                first_metric = list(fairness_results[model][sensitive_attribute].keys())[0]
                sub_groups = fairness_results[model][sensitive_attribute][first_metric][mode]
                individual_ct_groupBox.append(CorrespondenceTable(sub_groups))

            # metrics table
            metrics = fairness_results[model][sensitive_attribute]
            individual_metrics_groupBox.append(FairnessMetricsTable(metrics, mode, pl_type))

            # add to layout
            if len(individual_ct_groupBox) > 0:
                vBoxLayout.addWidget(individual_ct_groupBox[i])
            vBoxLayout.addWidget(individual_metrics_groupBox[i])
            vBoxLayout.addStretch()
            HBoxLayout.addWidget(individual_mode_groupBox[i])


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

        # 'Class' label
        labelClass = QtWidgets.QLabel()
        labelClass.setText("Class")
        labelClass.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelClass, 0, 0, alignment=Qt.AlignCenter)

        for j, sub_group in enumerate(sub_groups):
            # subgroup labels
            labelSubgroup = QtWidgets.QLabel()
            labelSubgroup.setText(str(sub_group).capitalize())
            tableGridLayout.addWidget(labelSubgroup, 0, j + 1, alignment=Qt.AlignCenter)

            confusion_matrix = sub_groups[sub_group]['confusion_matrix']
            n = int(np.sqrt(len(confusion_matrix)))
            cm = np.array(confusion_matrix).reshape(n, n)

            values = np.sum(cm, axis=0)
            for k, total in enumerate(values):
                # classes labels
                labelClass = QtWidgets.QLabel()
                labelClass.setText(str(k))
                labelClass.setStyleSheet("font-weight: bold")
                tableGridLayout.addWidget(labelClass, k + 1, 0, alignment=Qt.AlignCenter)
                # values labels 
                labelValue = QtWidgets.QLabel()
                labelValue.setText(str(total))
                labelValue.setStyleSheet("font-weight: bold")
                tableGridLayout.addWidget(labelValue, k + 1, j + 1, alignment=Qt.AlignCenter)


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

        # 'metric' label
        labelMetric = QtWidgets.QLabel()
        labelMetric.setText("Metric")
        labelMetric.setStyleSheet("font-weight: bold")
        tableGridLayout.addWidget(labelMetric, 0, 0, alignment=Qt.AlignCenter)

        if pl_type == "regression":
            # 'value' labels
            labelValue = QtWidgets.QLabel()
            labelValue.setText("Value")
            labelValue.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelValue, 0, 1, alignment=Qt.AlignCenter)

        for j, metric in enumerate(metrics):
            # fairness metrics labels
            labelMetric = QtWidgets.QLabel()
            labelMetric.setText(str(metric).capitalize())
            labelMetric.setStyleSheet("font-weight: bold")
            tableGridLayout.addWidget(labelMetric, j + 1, 0, alignment=Qt.AlignCenter)

            values = metrics[metric][mode]

            if pl_type == "classification":
                for k, value in enumerate(values):
                    measure = values[value]['affected_percent']
                    # subgroup labels
                    labelSubgroup = QtWidgets.QLabel()
                    labelSubgroup.setText(str(value).capitalize())
                    tableGridLayout.addWidget(labelSubgroup, 0, k + 1, alignment=Qt.AlignCenter)
                    # fairness measures
                    labelValue = QtWidgets.QLabel()
                    labelValue.setText(f"{measure:.3f}")
                    tableGridLayout.addWidget(labelValue, j + 1, k + 1, alignment=Qt.AlignCenter)

            if pl_type == "regression":
                # fairness measures
                labelValue = QtWidgets.QLabel()
                labelValue.setText(f"{values:.3f}")
                tableGridLayout.addWidget(labelValue, j + 1, 1, alignment=Qt.AlignCenter)
