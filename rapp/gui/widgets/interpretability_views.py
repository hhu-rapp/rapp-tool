from PyQt5 import QtWidgets, Qt, QtGui, QtCore
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.dbview import PandasModel
from rapp.gui.helper import CheckableComboBox
from rapp.gui.widgets import SummaryTable, PandasModelColor


class InitialView(QtWidgets.QWidget):
    def __init__(self, pipeline, model_callback):
        """
        Generates a widget to display the performance of the models in a table.

        Parameters
        ----------
        pipeline: rapp.pipeline object

        model_callback: function
            A reference to a function that is to be called when clicking the models on the table.
        """
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
    def __init__(self, pipeline, estimator, row_callback, mode_idx=None):
        """
        Generates a widget that displays all trained models with their corresponding predictive performances.

        Parameters
        ----------
        pipeline: rapp.pipeline object

        estimator: Trained classifier with predict_proba method

        row_callback: function
            A reference to a function that is to be called when clicking the rows of the table.
        """
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
        self.table_views = {}
        self.df = {}

        # load comoBox
        modes = list(self.pipeline.data.keys())
        for mode in modes:
            self.cbModes.addItem(str(mode).capitalize())
        if mode_idx is not None:
            self.cbModes.setCurrentIndex(mode_idx)

        def populate_predictions_tabs():
            self._populate_predictions_tabs(self.pipeline.data, estimator)

        self.cbModes.currentIndexChanged.connect(populate_predictions_tabs)

        self._populate_predictions_tabs(self.pipeline.data, estimator)

    def _populate_predictions_tabs(self, data_dict, model):
        self._clear_tabs()

        # get values from filters
        mode = self.cbModes.currentText().lower()

        # get dataframes from data
        data = data_dict[mode]
        target = data['y'].columns[0]
        pred_df = data['X'].copy()

        # predict and add to dataframe
        pred = model.predict_proba(pred_df)

        pred_df['Pred'] = pred.argmax(axis=1)
        pred_df['Proba'] = pred.max(axis=1).round(2)
        pred_df['Ground Truth'] = data['y']

        # create and populate a tableView for each label in a new tab
        for label in sorted(data['y'][target].unique()):
            self.df[label] = pred_df.loc[pred_df['Pred'] == label]

            self.table_views[label] = QtWidgets.QTableView(self)
            self.table_views[label].setSortingEnabled(True)
            self.table_views[label].resizeColumnsToContents()
            self.table_views[label].setSelectionBehavior(QtWidgets.QTableView.SelectRows)
            self.table_views[label].clicked.connect(self.row_callback_function)

            model = PandasModelColor(self.df[label])
            self.table_views[label].setModel(model)

            self.tabs.addTab(self.table_views[label], f'{target}={str(label)}')

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
        for _, widget in self.table_views.items():
            widget.setParent(None)
        self.filters.layout().removeItem(self.filters.layout().itemAt(0))
        self.filters.setParent(None)

    def clear_widget(self):
        self.setParent(None)

    def get_selected_df(self):
        # get dataframe from selected row
        tabs = list(self.table_views.keys())
        label = tabs[self.tabs.currentIndex()]
        model = self.table_views[label].model()
        selected_rows = self.table_views[label].selectionModel().selectedRows()

        selected_row = selected_rows[0].row()

        return model._df.iloc[[selected_row]]

    def get_mode_idx(self):
        return self.cbModes.currentIndex()


class ModelViewREG(ModelViewCLF):
    def __init__(self, pipeline, estimator, row_callback, mode_idx=None):
        """
        Generates a widget that displays the prediction information of the selected model.

        Parameters
        ----------
        pipeline: rapp.pipeline object

        estimator: Trained regressor with predict method

        row_callback: function
            A reference to a function that is to be called when clicking the rows of the table.
        """
        super(ModelViewREG, self).__init__(pipeline, estimator, row_callback, mode_idx=mode_idx)

    def _populate_predictions_tabs(self, data_dict, model):
        self._clear_tabs()

        # get values from filters
        mode = self.cbModes.currentText().lower()

        # get dataframes from data
        data = data_dict[mode]
        target = data['y'].columns[0]
        pred_df = data['X'].copy()

        # predict and add to dataframe
        pred_df['Pred'] = model.predict(pred_df).round(2)
        pred_df['Ground Truth'] = data['y'].round(2)

        self.df = pred_df

        # create and populate a tableView with dataframe
        self.table_view = QtWidgets.QTableView(self)
        self.table_view.setSortingEnabled(True)
        self.table_view.resizeColumnsToContents()
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table_view.clicked.connect(self.row_callback_function)

        model = PandasModel(self.df)
        self.table_view.setModel(model)

        # add to layout
        self.main_layout.addWidget(self.table_view)
        self.filters.layout().addRow('Mode:', self.cbModes)
        self.main_layout.addWidget(self.filters)

    def _clear_tabs(self):
        if hasattr(self, 'table_view'):
            self.table_view.setParent(None)
        self.filters.layout().removeItem(self.filters.layout().itemAt(0))
        self.filters.setParent(None)

    def get_selected_df(self):
        # get dataframe from selected row
        model = self.table_view.model()
        selected_rows = self.table_view.selectionModel().selectedRows()
        selected_row = selected_rows[0].row()

        return model._df.iloc[[selected_row]]


class SampleView(QtWidgets.QWidget):
    def __init__(self, pipeline, data_sample):
        """
        Generates a widget that allows closer inspection of predictions for a single element.

        Parameters
        ----------
        pipeline: rapp.pipeline object

        data_sample: dataframe
            Data sample to be analyzed
        """
        super(SampleView, self).__init__()

        self.pipeline = pipeline
        self.data_sample = data_sample
