from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.helper import CheckableComboBox
from rapp.gui.widgets import SummaryTable


class InitialView(QtWidgets.QWidget):

    def __init__(self, pipeline, model_callback):
        super(InitialView, self).__init__()

        self.pipeline = pipeline
        self.model_callback_function = model_callback

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # populate filters
        pl_type = self.pipeline.type.capitalize()

        # comboBox for filtering
        self.cbMetrics = CheckableComboBox()
        self.cbModes = QtWidgets.QComboBox()

        # groupBox for the filters
        self.filters_groupBox = QGroupBox("Filters")
        self.filters_groupBox.size()
        topLayout = QtWidgets.QFormLayout()
        self.filters_groupBox.setLayout(topLayout)

        # load comboBoxes
        performance_metrics = list(self.pipeline.score_functions.keys())
        for metric in performance_metrics:
            self.cbMetrics.addItem(str(metric))
        self.cbMetrics.check_items(performance_metrics)

        modes = list(self.pipeline.data.keys())
        for mode in modes:
            self.cbModes.addItem(str(mode).capitalize())

        def populate_summary_table():
            self._populate_summary_table(self.pipeline.performance_results, self.pipeline.type)

        self.cbMetrics.currentIndexChanged.connect(populate_summary_table)
        self.cbModes.currentIndexChanged.connect(populate_summary_table)

        # add to groupBox
        topLayout.addRow(f"{pl_type} Metrics:", self.cbMetrics)
        topLayout.addRow('Mode:', self.cbModes)

        # add to layout
        self.main_layout.addWidget(self.filters_groupBox)
        populate_summary_table()

    def _populate_summary_table(self, performance_results, pl_type):
        self._clear_table()
        # get values from filters
        mode = self.cbModes.currentText().lower()
        metrics = self.cbMetrics.get_checked_items()

        models = list(performance_results.keys())

        # create groupBox
        self.summary_groupBox = SummaryTable(mode, models, metrics, pl_type, metrics,
                                             performance_results)
        self.summary_groupBox.set_model_click_function(self.model_callback_function)

        # add to layout
        self.main_layout.addWidget(self.summary_groupBox)

    def _clear_table(self):
        try:
            self.summary_groupBox.setParent(None)
        except AttributeError:
            return

    def clear_widget(self):
        try:
            self.setParent(None)
        except AttributeError:
            return

