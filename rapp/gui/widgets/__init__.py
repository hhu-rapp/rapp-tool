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

