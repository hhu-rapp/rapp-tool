import os.path
import pathlib
import traceback

import joblib
# PyQt5
from PyQt5 import QtWidgets
# rapp gui
from PyQt5.QtCore import Qt

from rapp.gui.widgets.prediction_views import LoadModelView
import logging

log = logging.getLogger("prediction")


class PredictionWidget(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(PredictionWidget, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()
        self.setAcceptDrops(True)

    def initUI(self):
        # create layout
        self.vlayoutPrediction = QtWidgets.QVBoxLayout()
        self.vlayoutPrediction.setContentsMargins(0, 11, 0, 0)
        self.hlayoutTop = QtWidgets.QHBoxLayout()
        self.hlayoutTop.setContentsMargins(0, 0, 0, 22)
        self.featuresLayout = QtWidgets.QFormLayout()
        self.featuresLayout.setContentsMargins(0, 11, 11, 0)
        self.gridlayoutPrediction = QtWidgets.QGridLayout()
        self.menubuttonsPrediction = QtWidgets.QHBoxLayout()
        self.loadModelView = LoadModelView()

        self.vlayoutPrediction.addLayout(self.featuresLayout)
        self.vlayoutPrediction.addLayout(self.hlayoutTop)
        self.vlayoutPrediction.addWidget(self.loadModelView)
        self.vlayoutPrediction.addLayout(self.menubuttonsPrediction)

        # create buttons
        loadButton = QtWidgets.QPushButton('Load')
        loadButton.clicked.connect(self.showLoadModelDialog)
        loadButton.setStatusTip('Load trained model (Ctrl+l)')
        loadButton.setShortcut('Ctrl+l')
        loadButton.setFixedWidth(300)
        loadButton.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_FileIcon')))
        self.loadButton = loadButton

        predictButton = QtWidgets.QPushButton('Predict')
        predictButton.clicked.connect(self.predict)
        predictButton.setStatusTip('Predict SQL query with Models (Ctrl+P)')
        predictButton.setShortcut('Ctrl+p')
        self.predictButton = predictButton

        # add buttons
        self.hlayoutTop.addStretch()
        self.hlayoutTop.addWidget(self.loadButton, alignment=Qt.AlignLeft)
        self.hlayoutTop.addStretch()
        self.menubuttonsPrediction.addWidget(predictButton)

        self.setLayout(self.vlayoutPrediction)

    def dragEnterEvent(self, event):
        print('drag-enter')
        if event.mimeData().hasUrls():
            print('has urls')
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            file_extension = pathlib.Path(file_path).suffix

            if file_extension == '.joblib' or file_extension == '.h5':
                self._load_model(file_path)
            else:
                log.error(f'{file_extension} is not supported.')

    def predict(self):
        """
        Predicts selected data with the loaded Models.
        It assumes that the models loaded are compatible with the data.
        """
        data_df = self.qmainwindow.databasePredictionLayoutWidget.get_current_df()
        selected_indexes = self.qmainwindow.databasePredictionLayoutWidget.pandas_dataview.table.selectionModel().selectedIndexes()

        if data_df is None:
            log.error(f"No loaded data to predict from")
            return
        if len(self.loadModelView.loadedModels) == 0:
            log.error(f"No loaded models")
            return

        if len(selected_indexes) > 0:
            # selected_row = selected_indexes.rows()
            selected = [selected_index.row() for selected_index in selected_indexes]
            data_df = data_df.iloc[selected]
            log.debug(f"Student No. {selected} selected.")
            log.debug(f"Student's features: \n {data_df}")

        try:
            self.loadModelView.predict(data_df)
        except Exception as e:
            log.error(traceback.format_exc())
            traceback.print_exc()
            return

        log.info('Prediction finished.')

    def _load_model(self, filename):
        """
        Loads a .joblib model file and loads it to the comboBox[index].
        """
        model = joblib.load(filename)
        model_name = os.path.basename(filename)
        # models can be loaded as a dictionary
        if isinstance(model, dict):
            if model.get('uses_templates'):
                # get features
                if model.get('features_id', None) is not None:
                    if model.get('studies_id', None) is None:
                        features_id = model['features_id']
                    else:
                        features_id = f"{model['studies_id']}_{model['features_id']}"
                # get label
                if model.get('labels_id', None) is not None:
                    labels_id = model['labels_id']

                    current_f_id, current_l_id = self.qmainwindow.databasePredictionLayoutWidget.get_current_template_id()

                    if current_f_id != features_id or current_l_id != labels_id:
                        self.qmainwindow.databasePredictionLayoutWidget.sql_tabs.set_template_ids(f_id=features_id, l_id=labels_id)

                        if len(self.loadModelView.loadedModels) > 0:
                            log.warning("The data has been updated; Ensure that the loaded models are still compatible.")

            estimator = model['model']

        else:
            estimator = model

        df = self.qmainwindow.databasePredictionLayoutWidget.get_current_df()
        pos_targets = df.columns.tolist()

        self.loadModelView.load_model(estimator, model_name, pos_targets)
        self.loadModelView.update_labels(pos_targets)

    def showLoadModelDialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Trained Model", "",
                                                            "Joblib Files (*.joblib);; H5 Files (*.h5);;All Files (*)",
                                                            options=options)
        if fileName:
            self._load_model(fileName)

    def refresh_labels(self):
        df = self.qmainwindow.databasePredictionLayoutWidget.get_current_df()
        pos_targets = df.columns.tolist()

        self.loadModelView.update_labels(pos_targets)
