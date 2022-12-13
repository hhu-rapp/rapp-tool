import os
import re

from PyQt5 import QtWidgets, Qt, QtGui, QtCore
from PyQt5.QtWidgets import QGroupBox, QScrollArea
import matplotlib
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.tree._tree import TREE_LEAF

from rapp.gui.dbview import PandasModel
from rapp.gui.helper import CheckableComboBox
from rapp.gui.widgets import SummaryTable, PandasModelColor
from rapp.util import estimator_name


class InitialView(QtWidgets.QWidget):
    def __init__(self, pipeline, model_callback):
        """
        Generates a widget to display all trained models with their corresponding predictive performances.

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

        self.stretch = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)

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
        self.main_layout.addItem(self.stretch)

    def _clear_table(self):
        try:
            self.summary_table.setParent(None)
            self.main_layout.removeItem(self.stretch)
        except AttributeError:
            return

    def clear_widget(self):
        try:
            self.setParent(None)
        except AttributeError:
            return

    def get_mode_idx(self):
        return self.cbModes.currentIndex()

    def set_mode_idx(self, mode_idx):
        self.cbModes.setCurrentIndex(mode_idx)


class ModelViewCLF(QtWidgets.QWidget):
    def __init__(self, pipeline, estimator, row_callback):
        """
        Generates a widget that displays all trained models with their corresponding predictive performances.

        Parameters
        ----------
        pipeline: rapp.pipeline object

        estimator: Trained classifier with predict_proba method.

        row_callback: function
            A reference to a function that is to be called when clicking the rows of the table.
        """
        super(ModelViewCLF, self).__init__()

        self.pipeline = pipeline
        self.estimator = estimator
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

        # visualization of estimators
        if estimator_name(estimator) in ('DecisionTreeClassifier', 'DecisionTreeRegressor'):
            data = self.pipeline.data['train']
            target = data['y'].columns[0]
            features = data['X'].columns.tolist()

            buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_header_widget = QtWidgets.QWidget()
            self.buttons_header_widget.setLayout(buttons_layout)

            button_visualize = QtWidgets.QPushButton('Visualize Estimator')
            button_visualize.setIcon(self.style().standardIcon(
                getattr(QtWidgets.QStyle, 'SP_FileDialogDetailedView')))
            button_visualize.setStatusTip('Visualize estimator')
            button_visualize.setMaximumWidth(200)

            button_save = QtWidgets.QPushButton('Save Visualization')
            button_save.setIcon(self.style().standardIcon(
                getattr(QtWidgets.QStyle, 'SP_DialogSaveButton')))
            button_save.setStatusTip('Save estimator visualization as PDF file')
            button_save.setMaximumWidth(200)

            # generate visualization plot
            self.fig = self._generate_estimator_visualization(estimator, features, target)

            button_visualize.clicked.connect(self.fig.show)
            button_save.clicked.connect(self._show_save_plot_dialog)

            # add to layout
            buttons_layout.addWidget(button_visualize, alignment=QtCore.Qt.AlignRight)
            buttons_layout.addWidget(button_save, alignment=QtCore.Qt.AlignRight)

            self.main_layout.addWidget(self.buttons_header_widget, alignment=QtCore.Qt.AlignRight)

        def populate_predictions_tabs():
            self._populate_predictions_tabs(self.pipeline.data, self.estimator)

        self.cbModes.currentIndexChanged.connect(populate_predictions_tabs)

        self._populate_predictions_tabs(self.pipeline.data, self.estimator)

    def _populate_predictions_tabs(self, data_dict, estimator):
        self._clear_tabs()

        # get values from filters
        mode = self.cbModes.currentText().lower()

        # get dataframes from data
        data = data_dict[mode]
        target = data['y'].columns[0]
        pred_df = data['X'].copy()

        # predict and add to dataframe
        pred = estimator.predict_proba(pred_df)

        pred_df['Pred'] = pred.argmax(axis=1)
        pred_df['Proba'] = pred.max(axis=1).round(2)
        pred_df['Ground Truth'] = data['y']

        # create and populate a tableView for each label in a new tab
        for label in sorted(data['y'][target].unique()):
            self.df[label] = pred_df.loc[pred_df['Pred'] == label]

            self.table_views[label] = QtWidgets.QTableView(self)
            self.table_views[label].setSortingEnabled(True)
            self.table_views[label].setSelectionBehavior(QtWidgets.QTableView.SelectRows)
            self.table_views[label].clicked.connect(self.row_callback_function)

            model = PandasModelColor(self.df[label])
            self.table_views[label].setModel(model)

            header = self.table_views[label].horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

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
        # get dataframe and probabilities from selected row
        tabs = list(self.table_views.keys())
        label = tabs[self.tabs.currentIndex()]
        model = self.table_views[label].model()
        selected_rows = self.table_views[label].selectionModel().selectedRows()

        selected_row = selected_rows[0].row()

        df = model.df.iloc[[selected_row]]
        probabilities = self.estimator.predict_proba(df.iloc[:, :-3])

        return df, probabilities

    def get_mode_idx(self):
        return self.cbModes.currentIndex()

    def set_mode_idx(self, mode_idx):
        self.cbModes.setCurrentIndex(mode_idx)

    def get_tab_idx(self):
        return self.tabs.currentIndex()

    def set_tab_idx(self, mode_idx):
        self.tabs.setCurrentIndex(mode_idx)

    def _generate_estimator_visualization(self, estimator, features, target):
        if estimator_name(estimator) in ('DecisionTreeClassifier', 'DecisionTreeRegressor'):
            plt.close("all")
            plt.figure(figsize=(20, 10))
            targets = [f"No-{target}", target] if estimator.n_classes_ == 2 else None
            tree.plot_tree(estimator, feature_names=features, class_names=targets, label='none',
                           impurity=False, filled=True, proportion=True,
                           max_depth=3,
                           fontsize=8)
            plt.title(f'{target} - Decision Tree Visualization')

        return plt.gcf()

    def _show_save_plot_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Trained Model as a File",
                                                            'decision_tree_visualization',
                                                            "PDF Files (*.pdf);;All Files (*)", options=options)
        if fileName:
            filename = (f'{fileName}.pdf' if fileName.split('.')[-1] != 'pdf' else fileName)
            self._save_plot(filename)

    def _save_plot(self, filename):
        # TODO: Bug with Title
        size = self.fig.get_size_inches()  #* plot.figure.dpi
        self.fig.set_size_inches(5, 3.5)
        title = self.fig.axes[0].get_title()
        plt.title('')
        self.fig.savefig(filename, bbox_inches="tight")
        # reset settings
        plt.title(title)
        self.fig.set_size_inches(size)  # return back to original size after exporting plot


class ModelViewREG(ModelViewCLF):
    def __init__(self, pipeline, estimator, row_callback):
        """
        Generates a widget that displays the prediction information of the selected model.

        Parameters
        ----------
        pipeline: rapp.pipeline object

        estimator: Trained regressor with predict method.

        row_callback: function
            A reference to a function that is to be called when clicking the rows of the table.
        """
        super(ModelViewREG, self).__init__(pipeline, estimator, row_callback)

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

        return model.df.iloc[[selected_row]], None


class SampleView(QtWidgets.QWidget):
    def __init__(self, data_sample, probabilities=None):
        """
        Generates a widget that allows closer inspection of predictions for a single element.

        Parameters
        ----------
        data_sample: dataframe
            Data sample to be analyzed

        probabilities: array-like of shape (n_samples, n_classes), optional
            Predicted probabilities for the sample.
        """
        super(SampleView, self).__init__()

        self.data_sample = data_sample

        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        # Layout for the sample entries
        self.entries_layout = QtWidgets.QGridLayout()
        self.entries_layout.setContentsMargins(10, 10, 50, 10)
        # Scroll Area for entries
        self.entries_widget = QtWidgets.QWidget()
        self.entries_widget.setLayout(self.entries_layout)
        self.entries_scroll = QScrollArea()
        self.entries_scroll.setWidgetResizable(True)
        self.entries_scroll.setWidget(self.entries_widget)

        self.entries_scroll.setStyleSheet("QScrollArea{background-color: white}"
                                         "QWidget#WhiteBackground {background-color: white}")
        self.entries_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.entries_widget.setObjectName("WhiteBackground")

        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.setContentsMargins(50, 10, 100, 150)
        self.right_widget = QtWidgets.QWidget()
        self.right_widget.setLayout(self.right_layout)

        self.predictions_layout = QtWidgets.QHBoxLayout()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Layout for the probability values table
        self.proba_layout = QtWidgets.QGridLayout()
        self.proba_layout.setColumnStretch(0, 2)
        self.proba_layout.setColumnStretch(1, 1)
        self.proba_layout.setContentsMargins(10, 10, 50, 10)
        # Layout for the ground truth and predicted label
        self.pred_layout = QtWidgets.QVBoxLayout()
        self.pred_layout.setContentsMargins(10, 10, 50, 10)

        self.button_explanation = QtWidgets.QPushButton('Generate Explanation')
        self.button_explanation.clicked.connect(self._generate_explanation)
        self.button_explanation.setStatusTip('Generate Explanation')
        self.button_explanation.setEnabled(False)

        self.button_counterfactuals = QtWidgets.QPushButton('Generate Counterfactuals')
        self.button_counterfactuals.clicked.connect(self._generate_counterfactuals)
        self.button_counterfactuals.setStatusTip('Generate Counterfactuals')
        self.button_counterfactuals.setEnabled(False)

        # Dicts for the QtLabels
        self.entries_labels = {}
        self.proba_labels = {}

        # Classification
        if probabilities is not None:
            self._populate_entries_labels(data_sample.iloc[:, :-3])
            self._populate_pred_tables(data_sample.iloc[:, -3:], probabilities)
        # Regression
        if probabilities is None:
            self._populate_entries_labels(data_sample.iloc[:, :-2])
            self._populate_pred_tables(data_sample.iloc[:, -2:], probabilities)

        # add to layout
        splitter.addWidget(self.entries_scroll)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([480, 800])
        self.main_layout.addWidget(splitter)
        self.right_layout.addLayout(self.predictions_layout)
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.button_explanation)
        self.right_layout.addWidget(self.button_counterfactuals)
        self.predictions_layout.addLayout(self.proba_layout)
        self.predictions_layout.addLayout(self.pred_layout)
        self.predictions_layout.addStretch()

    def _populate_entries_labels(self, sample):
        # Labels are stored in a dict with title label as key
        entriesLabel = QtWidgets.QLabel()
        entriesLabel.setText('Feature')
        entriesLabel.setStyleSheet('font-weight: bold;')
        self.entries_layout.addWidget(entriesLabel, 0, 0)

        valuesLabel = QtWidgets.QLabel()
        valuesLabel.setText('Value')
        valuesLabel.setStyleSheet('font-weight: bold;')
        self.entries_layout.addWidget(valuesLabel, 0, 1)

        # Entry labels stored in a list
        self.entries_labels[entriesLabel] = []
        self.entries_labels[valuesLabel] = []
        for i, (feature, value) in enumerate(sample.to_dict(orient='records')[0].items()):
            featureLabel = QtWidgets.QLabel()
            featureLabel.setText(str(feature))

            valueLabel = QtWidgets.QLabel()
            valueLabel.setText(f'{value:.3f}')

            self.entries_layout.addWidget(featureLabel, i + 1, 0)
            self.entries_layout.addWidget(valueLabel, i + 1, 1)
            self.entries_labels[entriesLabel].append(featureLabel)
            self.entries_labels[valuesLabel].append(valueLabel)

    def _populate_pred_tables(self, sample_pred, probabilities=None):
        self.pred_label = QtWidgets.QLabel()
        self.pred_label.setText(f'Prediction: {sample_pred["Pred"].iloc[0]}')
        self.pred_layout.addWidget(self.pred_label)

        self.ground_truth_label = QtWidgets.QLabel()
        self.ground_truth_label.setText(f'Ground Truth: {sample_pred["Ground Truth"].iloc[0]}')
        self.pred_layout.addWidget(self.ground_truth_label)

        # Classification
        if probabilities is not None:
            # Highlight misclassification
            if sample_pred["Pred"].iloc[0] != sample_pred["Ground Truth"].iloc[0]:
                self.pred_label.setStyleSheet('color : red;')

            # QtLabels stored in a dict with title label as key
            labelLabel = QtWidgets.QLabel()
            labelLabel.setText('Label')
            labelLabel.setStyleSheet('font-weight: bold;')
            self.proba_layout.addWidget(labelLabel, 0, 0, alignment=QtCore.Qt.AlignLeft)

            probaLabel = QtWidgets.QLabel()
            probaLabel.setText("Probability")
            probaLabel.setStyleSheet('font-weight: bold;')
            self.proba_layout.addWidget(probaLabel, 0, 1, alignment=QtCore.Qt.AlignRight)

            # Pred and Proba values stored in a list
            self.proba_labels[labelLabel] = []
            self.proba_labels[probaLabel] = []
            for label, proba in enumerate(probabilities[0]):
                labelValue = QtWidgets.QLabel()
                labelValue.setText(str(label))
                self.proba_labels[labelLabel].append(labelValue)
                self.proba_layout.addWidget(labelValue, label + 1, 0, alignment=QtCore.Qt.AlignLeft)

                probaValue = QtWidgets.QLabel()
                probaValue.setText(str(proba.round(2)))
                self.proba_labels[probaLabel].append(labelValue)
                self.proba_layout.addWidget(probaValue, label + 1, 1, alignment=QtCore.Qt.AlignRight)

    def clear_widget(self):
        self.setParent(None)

    def _generate_explanation(self):
        pass

    def _generate_counterfactuals(self):
        pass
