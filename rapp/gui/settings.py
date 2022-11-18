# PyQt5
import joblib
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from rapp.gui.pipeline import Pipeline
from rapp.util import estimator_name

import logging
log = logging.getLogger('GUI')


class SimpleSettings(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(SimpleSettings, self).__init__()

        self.qmainwindow = qmainwindow
        self.initUI()
        self.pipeline = None
        self.data_settings = None

    def initUI(self):
        # create layout
        vLayout = QtWidgets.QVBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vLayout)

        # create widgets
        self.tab = QtWidgets.QTabWidget()
        self.simple_tab = Pipeline(self.qmainwindow)

        # add widgets to tab
        self.tab.addTab(self.simple_tab, 'Settings')
        self.__init_trainedModels_tab()

        # add widgets to layout
        vLayout.addWidget(self.tab, 3)
        vLayout.addWidget(self.qmainwindow.loggingTextBrowser, 1)

    def __init_trainedModels_tab(self):
        self.individual_tab = QtWidgets.QWidget()
        self.individual_tab.setLayout(QtWidgets.QVBoxLayout())
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(11, 11, 11, 0)

        # add labels
        labelFeatures = QtWidgets.QLabel()
        labelFeatures.setText("Feature_id: ")
        labelLabels = QtWidgets.QLabel()
        labelLabels.setText("Label_id: ")

        self.featuresIdLabel = QtWidgets.QLabel()
        self.featuresIdLabel.setText("-")
        self.labelsIdLabel = QtWidgets.QLabel()
        self.labelsIdLabel.setText("-")

        labelModels = QtWidgets.QLabel()
        labelModels.setText("Model: ")
        self.cbModels = QtWidgets.QComboBox()
        self.cbModels.clear()

        saveButton = QtWidgets.QPushButton('Save Model')
        saveButton.clicked.connect(self.saveModel)
        saveButton.setStatusTip('Save Selected model')

        self.gridLayout.addWidget(labelModels, 2, 0)
        self.gridLayout.addWidget(self.cbModels, 2, 1)
        self.gridLayout.addWidget(saveButton, 2, 2)

        self.gridLayout.addWidget(labelFeatures, 0, 0)
        self.gridLayout.addWidget(self.featuresIdLabel, 0, 1, alignment=QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(labelLabels, 1, 0)
        self.gridLayout.addWidget(self.labelsIdLabel, 1, 1, alignment=QtCore.Qt.AlignCenter)

        self.individual_tab.layout().addLayout(self.gridLayout)
        self.individual_tab.layout().setAlignment(QtCore.Qt.AlignTop)

        tab_idx = self.tab.addTab(self.individual_tab, 'Save Models')
        self.individual_tab_idx = tab_idx
        self.tab.setTabEnabled(tab_idx, False)

    def refresh_data(self, pipeline, data_settings):
        self.data_settings = data_settings
        self.pipeline = pipeline

        self.cbModels.clear()

        self.featuresIdLabel.setText(f"{data_settings['studies_id']}_{data_settings['features_id']}")
        self.labelsIdLabel.setText(data_settings['labels_id'])

        for model in self.pipeline.fairness_results:
            self.cbModels.addItem(estimator_name(model))

    def saveModel(self):
        """
        The Model is saved in a dictionary as a .joblib file

        {'model' : trained estimator,
        'studies_id': studies_id of train data,
        'features_id': features_id of train data,
        'labels_id': predicting label_id of the model}
        """
        if self.pipeline is None:
            log.error("There are currently no models in the pipeline")
            return

        model_idx = self.cbModels.currentIndex()

        file_name = ""
        for col_id in self.data_settings:
            label = self.data_settings[col_id]
            file_name += f"{label}_"

        file_name += self.cbModels.currentText()

        self.data_settings['model'] = list(self.pipeline.fairness_results.keys())[model_idx]

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Trained Model as a File", "",
                                                            "Joblib Files (*.joblib);;All Files (*)", options=options)

        if fileName:
            joblib.dump(self.data_settings, f"{fileName}.joblib")
