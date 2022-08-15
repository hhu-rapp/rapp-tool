from PyQt5 import QtWidgets, Qt, QtGui, QtCore
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.dbview import PandasModel
from rapp.gui.helper import CheckableComboBox
from rapp.gui.widgets import SummaryTable, PandasModelColor


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
        self.summary_table = SummaryTable(mode, models, metrics, pl_type, metrics,
                                             performance_results)
        self.summary_table.set_model_click_function(self.model_callback_function)

        # add to layout
        self.main_layout.addWidget(self.summary_table)

    def _clear_table(self):
        try:
            self.summary_table.setParent(None)
        except AttributeError:
            return

    def clear_widget(self):
        try:
            self.setParent(None)
        except AttributeError:
            return

    def get_mode_idx(self):
        return self.cbModes.currentIndex()


class ModelViewCLF(QtWidgets.QWidget):

    def __init__(self, pipeline, model, row_callback, mode_idx=None):
        super(ModelViewCLF, self).__init__()

        self.pipeline = pipeline
        self.row_callback_function = row_callback

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.filters = QtWidgets.QWidget()
        self.filters.setLayout(QtWidgets.QFormLayout())

        # comboBox for filtering
        self.cbModes = QtWidgets.QComboBox()

        self.tabs = QtWidgets.QTabWidget()

        # load comoBox
        modes = list(self.pipeline.data.keys())
        for mode in modes:
            self.cbModes.addItem(str(mode).capitalize())
        if mode_idx is not None:
            self.cbModes.setCurrentIndex(mode_idx)

        def populate_predictions_tabs():
            self._populate_predictions_tabs(self.pipeline.data, model)

        self.cbModes.currentIndexChanged.connect(populate_predictions_tabs)

        self.tabs_list = {}
        self.df = {}
        self._populate_predictions_tabs(self.pipeline.data, model)

    def _populate_predictions_tabs(self, data_dict, model):
        self._clear_tabs()

        # get values from filters
        mode = self.cbModes.currentText().lower()

        data = data_dict[mode]

        target = data['y'].columns[0]

        pred_df = data['X'].copy()

        pred = model.predict_proba(pred_df)

        pred_df['Pred'] = pred.argmax(axis=1)
        pred_df['Proba'] = pred.max(axis=1).round(2)
        pred_df['Ground Truth'] = data['y']

        for label in sorted(data['y'][target].unique()):
            self.df[label] = pred_df.loc[pred_df['Pred'] == label]

            self.tabs_list[label] = QtWidgets.QTableView(self)
            self.tabs_list[label].setSortingEnabled(True)
            self.tabs_list[label].resizeColumnsToContents()
            model = PandasModelColor(self.df[label])

            self.tabs_list[label].setModel(model)

            self.tabs.addTab(self.tabs_list[label], f'{target}={str(label)}')
            def highlight_misclassifications():
                self._highlight_misclassifications(self.tabs.currentIndex())

            self._highlight_misclassifications(self.tabs.indexOf(self.table_views[label]))
            model.layoutChanged.connect(highlight_misclassifications)

        # add to layout
        self.main_layout.addWidget(self.tabs)
        self.filters.layout().addRow('Mode:', self.cbModes)
        self.main_layout.addWidget(self.filters)

    def _highlight_misclassifications(self, tab_idx):
        # get abstractTableModel of tab
        tabs = list(self.table_views.keys())
        label = tabs[tab_idx]
        model = self.table_views[label].model()

        self._reset_colors(model)
        row_count = model.rowCount()
        # FIXME: Hardcoded indices for the columns
        ground_truth_col = model.columnCount() - 1
        pred_col = model.columnCount() - 3

        # highlight misclassification in different color
        for rowNumber in range(row_count):
            ground_truth_index = model.index(rowNumber, ground_truth_col)
            ground_truth_data = model.data(ground_truth_index, QtCore.Qt.DisplayRole)

            pred_col_index = model.index(rowNumber, pred_col)
            pred_col_data = model.data(pred_col_index, QtCore.Qt.DisplayRole)

            if int(ground_truth_data.value()) != int(pred_col_data.value()):
                for cellColumn in range(model.columnCount()):
                    model.change_color(rowNumber, cellColumn, QtGui.QBrush(QtGui.QColor(255, 0, 0, 100)))

    def _reset_colors(self, model):
        # set background color of all rows to white
        row_count = model.rowCount()
        for rowNumber in range(row_count):
            for cellColumn in range(model.columnCount()):
                model.change_color(rowNumber, cellColumn, QtGui.QBrush(QtGui.QColor(255, 255, 255)))

    def _clear_tabs(self):
        for _, widget in self.tabs_list.items():
            widget.setParent(None)
        self.filters.layout().removeItem(self.filters.layout().itemAt(0))
        self.filters.setParent(None)

    def clear_widget(self):
        try:
            self.setParent(None)
        except AttributeError:
            return


class ModelViewREG(ModelViewCLF):

    def __init__(self, pipeline, model, row_callback, mode_idx=None):
        super(ModelViewREG, self).__init__(pipeline, model, row_callback, mode_idx=None)

    def _populate_predictions_tabs(self, data_dict, model):
        self._clear_tabs()

        # get values from filters
        mode = self.cbModes.currentText().lower()

        data = data_dict[mode]

        target = data['y'].columns[0]

        pred_df = data['X'].copy()

        pred_df['Pred'] = model.predict(pred_df).round(2)
        pred_df['Ground Truth'] = data['y']

        self.df = pred_df

        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setSortingEnabled(True)
        self.table_view.resizeColumnsToContents()

        model = PandasModel(self.df)
        self.table_view.setModel(model)

        # add to layout
        self.main_layout.addWidget(self.table_view)
        self.filters.layout().addRow('Mode:', self.cbModes)
        self.main_layout.addWidget(self.filters)

    def _clear_tabs(self):
        try:
            self.table_view.setParent(None)
        except AttributeError:
            return

        self.filters.layout().removeItem(self.filters.layout().itemAt(0))
        self.filters.setParent(None)
