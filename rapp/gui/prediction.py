import os.path
from os import listdir, getcwd
from os.path import isdir, join, abspath

import joblib
# PyQt5
import numpy as np
from PyQt5 import QtWidgets
# rapp gui
from PyQt5.QtCore import Qt
from scipy import stats

from rapp import sqlbuilder
from rapp.gui.helper import LoadModelPushButton, CheckableComboBox
from rapp.pipeline import preprocess_data

import logging
log = logging.getLogger("prediction")


class PredictionWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(PredictionWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()

    def initUI(self):
        # create layout
        self.vlayoutPrediction = QtWidgets.QVBoxLayout()
        self.vlayoutPrediction.setContentsMargins(25, 11, 0, 0)
        self.featuresLayout = QtWidgets.QFormLayout()
        self.featuresLayout.setContentsMargins(0,11,11,22)
        self.gridlayoutPrediction = QtWidgets.QGridLayout()
        self.menubuttonsPrediction = QtWidgets.QHBoxLayout()

        self.vlayoutPrediction.addLayout(self.featuresLayout)
        self.vlayoutPrediction.addLayout(self.gridlayoutPrediction)
        self.vlayoutPrediction.addStretch(1)
        self.vlayoutPrediction.addLayout(self.menubuttonsPrediction)

        # create buttons
        predictButton = QtWidgets.QPushButton('Predict')
        predictButton.clicked.connect(self.predict)
        predictButton.setStatusTip('Predict SQL query with Models (Ctrl+P)')
        predictButton.setShortcut('Ctrl+p')
        self.predictButton = predictButton

        clearButton = QtWidgets.QPushButton('Clear')
        clearButton.clicked.connect(self.clear_loaded_models)
        clearButton.setStatusTip('Clear all loaded models')
        self.clearButton = clearButton

        # add pred button
        self.menubuttonsPrediction.addWidget(predictButton)

        # headers
        headers = ['Load', 'Model', 'Target', 'Prediction', 'Mean Student']

        # get labels
        self.label_ids = sqlbuilder.list_available_labels()
        self.label_ids.sort()
        # create lists for widgets
        self.predLabels = []
        self.loadedModelsCb = []
        self.loadModelButtons = []

        # add headers
        self.featuresIdLabel = QtWidgets.QLabel()
        self.featuresIdLabel.setText("")

        for i, header in enumerate(headers):
            headerLabel = QtWidgets.QLabel()
            headerLabel.setText(header)
            headerLabel.setStyleSheet("font-weight: bold")
            self.gridlayoutPrediction.addWidget(headerLabel, 0, i, alignment=Qt.AlignCenter)

        self.featuresLayout.addRow('Features:', self.featuresIdLabel)

        # add rows
        for i, target in enumerate(self.label_ids):
            targetLabel = QtWidgets.QLabel()
            targetLabel.setText(target)

            predLabel = QtWidgets.QLabel()
            predLabel.setText("-")

            loadModelButton = LoadModelPushButton(i)
            # Load model buttons and predLabel are saved in a list
            self.loadModelButtons.append(loadModelButton)
            self.loadModelButtons[i].set_click_function(self.showLoadModelDialog)
            self.predLabels.append(predLabel)
            self.loadedModelsCb.append(CheckableComboBox())
            # add widgets
            self.gridlayoutPrediction.addWidget(self.loadModelButtons[i], i+1, 0)
            self.gridlayoutPrediction.addWidget(self.loadedModelsCb[i], i+1, 1)
            self.gridlayoutPrediction.addWidget(targetLabel, i+1, 2, alignment=Qt.AlignCenter)
            self.gridlayoutPrediction.addWidget(self.predLabels[i], i+1, 3, alignment=Qt.AlignCenter)

        self.gridlayoutPrediction.addWidget(self.clearButton, i+2, 0, 1, 2, alignment=Qt.AlignCenter)

        self.setLayout(self.vlayoutPrediction)

    def predict(self):
        """
        Predicts selected data with the loaded and selected Models.
        It assumes that the models loaded are compatible with the data.
        """
        data_df, data_f_id, data_l_id = self.qmainwindow.databasePredictionLayoutWidget.getDataSettings()
        selected_indexes = self.qmainwindow.databasePredictionLayoutWidget.pandas_dataview.table.selectionModel().selectedIndexes()

        if data_df is None or data_f_id is None or data_l_id is None:
            log.error(f"No valid data to predict")
            return

        # drop last column
        data_df = data_df.iloc[:, :-1]

        X = preprocess_data(data_df, data_df.select_dtypes(exclude=["number"]).columns)
        if len(selected_indexes) > 0:
            selected_row = selected_indexes[0].row()
            X = X.iloc[[selected_row]]
            log.error(f"Student No. {selected_row} selected.")
            log.error(f"Student's features: \n {X}")

        for i, modelCb in enumerate(self.loadedModelsCb):
            models = modelCb.get_checked_items()

            if models is None:
                log.error(f"No Model Selected")
                return
            else:
                y_preds = []
                for model in models:
                    item_index = modelCb.find_item_index(model)
                    y_preds.append(modelCb.itemData(item_index)['model'].predict(X))

                if modelCb.itemData(item_index) is not None:
                    # Majority voting for classification
                    if modelCb.itemData(item_index)['labels_id'].split('_')[0] != 'reg':
                        y_pred = stats.mode(np.array(y_preds))
                        self.predLabels[i].setText(str(y_pred[0]))
                    # Mean for regression
                    if modelCb.itemData(item_index)['labels_id'].split('_')[0] == 'reg':
                        y_pred = np.mean(np.array(y_preds))
                        self.predLabels[i].setText(str(y_pred))

                log.error('Prediction finished.')

    def load_model(self, filename, index):
        """
        Loads a .joblib model file and loads it to the comboBox[index].
        """
        model = joblib.load(filename)

        # Verify models compatibility
        _, data_f_id, _ = self.qmainwindow.databasePredictionLayoutWidget.getDataSettings()
        # same features as data
        if data_f_id != f"{model['studies_id']}_{model['features_id']}":
            log.error(f"Model trained with {model['studies_id']}_{model['features_id']} "
                      f"is not compatible with {data_f_id}")
            return
        # same label
        if self.label_ids[index] != model['labels_id']:
            log.error(f"Model trained with {model['labels_id']} is not compatible with {self.label_ids[index]}")
            return

        modelName = os.path.basename(filename)
        # append loaded model
        self.loadedModelsCb[index].addItem(str(modelName), userData=model)
        item_index = self.loadedModelsCb[index].find_item_index(str(modelName))
        self.loadedModelsCb[index].setItemChecked(item_index)

    def showLoadModelDialog(self, index):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Config File", "",
                                                            "Joblib Files (*.joblib);;All Files (*)",
                                                            options=options)
        if fileName:
            self.load_model(fileName, index)

    def clear_loaded_models(self):
        for modelCb in self.loadedModelsCb:
            modelCb.clear()

    def refresh_labels(self):
        self.clear_loaded_models()

        _, f_id, _ = self.qmainwindow.databasePredictionLayoutWidget.getDataSettings()
        self.featuresIdLabel.setText(f_id)
