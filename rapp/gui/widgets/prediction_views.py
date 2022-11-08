import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from scipy.stats import stats

from rapp.gui.helper import IdButton


class LoadModelView(QtWidgets.QWidget):
    def __init__(self):
        """
        Generates a widget to display all trained models with their corresponding predictive performances.
        """
        super(LoadModelView, self).__init__()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        self.headersLayout = QtWidgets.QHBoxLayout()
        self.predVBoxLayout = QtWidgets.QVBoxLayout()
        self.predWidget = QtWidgets.QWidget()
        self.pred_scroll = QtWidgets.QScrollArea()

        self.loadedModels = []
        self.ensembleLabels = {}
        self.ensembleLayouts = []

        # add default text
        self.defaultTextLabel = QtWidgets.QLabel()
        self.defaultTextLabel.setText("Drop your files here")
        self.defaultTextLabel.setAlignment(QtCore.Qt.AlignCenter)

        # add headers
        self.modelLabel = QtWidgets.QLabel()
        self.modelLabel.setText("Model")
        self.modelLabel.setStyleSheet("font-weight: bold")

        self.targetLabel = QtWidgets.QLabel()
        self.targetLabel.setText("Target")
        self.targetLabel.setStyleSheet("font-weight: bold")
        self.targetLabel.setFixedWidth(150)

        self.predLabel = QtWidgets.QLabel()
        self.predLabel.setText("Prediction")
        self.predLabel.setStyleSheet("font-weight: bold")
        self.predLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.predLabel.setFixedWidth(150)

        self.probaLabel = QtWidgets.QLabel()
        self.probaLabel.setText("Proba")
        self.probaLabel.setStyleSheet("font-weight: bold")
        self.probaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.probaLabel.setFixedWidth(150)

        self.ensembleLabel = QtWidgets.QLabel()
        self.ensembleLabel.setText("Ensemble Learning")
        self.ensembleLabel.setStyleSheet("font-weight: bold")

        self.predStretch = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Expanding)

        self.headersLayout.addWidget(self.modelLabel, 0, QtCore.Qt.AlignCenter)
        self.headersLayout.addStretch()
        self.headersLayout.addWidget(self.targetLabel, 0, QtCore.Qt.AlignCenter)

        self.predWidget.setLayout(self.predVBoxLayout)

        # add scroll area
        self.pred_scroll.setWidgetResizable(True)
        self.pred_scroll.setWidget(self.predWidget)
        self.pred_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)

        # add to layout
        self.predVBoxLayout.addLayout(self.headersLayout)
        self.stretch_models = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                    QtWidgets.QSizePolicy.Expanding)
        self.predVBoxLayout.addItem(self.stretch_models)

        self.main_layout.addWidget(self.defaultTextLabel)
        self.main_layout.setAlignment(QtCore.Qt.AlignCenter)

    def load_model(self, model, model_name, labels):
        index = len(self.loadedModels)

        # first model is loaded
        if index == 0:
            # remove default text
            self.defaultTextLabel.setParent(None)

            # add scroll area to layout
            self.main_layout.addWidget(self.pred_scroll)
            self.main_layout.setAlignment(QtCore.Qt.AlignTop)

        # create model widget
        widget = LoadedModelWidget(model, model_name, labels, index)
        widget.removeButton.set_click_function(self._remove_model)

        # add to layout
        self.predVBoxLayout.removeItem(self.stretch_models)
        self.loadedModels.append(widget)
        self.predVBoxLayout.addWidget(widget)
        self.predVBoxLayout.addItem(self.stretch_models)

    def predict(self, data):
        self._clear_ensemble_labels()
        # add pred headers
        self.headersLayout.addItem(self.predStretch)
        self.headersLayout.addWidget(self.predLabel, 0, QtCore.Qt.AlignCenter)
        self.headersLayout.addWidget(self.probaLabel, 0, QtCore.Qt.AlignCenter)

        ensemble = {}
        for model in self.loadedModels:
            model.predict(data)

            # ensemble learning
            target = model.cbTarget.currentText()
            if model.probaLabel.text() == '-':
                ml_type = 'regression'
                if ensemble.get(ml_type) is None:
                    ensemble[ml_type] = {}

            elif model.probaLabel.text() != '-':
                ml_type = 'classification'
                if ensemble.get(ml_type) is None:
                    ensemble[ml_type] = {}

            # group prediction by target and type
            if ensemble[ml_type].get(target) is None:
                ensemble[ml_type][target] = []

            ensemble[ml_type][target].append(np.float(model.predLabel.text()))

        self.ensembleLabel.setText('Ensemble Learning')
        self.predVBoxLayout.addWidget(self.ensembleLabel, 0, QtCore.Qt.AlignCenter)

        for ensemble_type, targets in ensemble.items():
            # mean for regression, majority voting for classification
            if ensemble_type == 'regression':
                ensemble_func = np.mean
            elif ensemble_type == 'classification':
                ensemble_func = lambda x: stats.mode(x)[0][0]

            for target, preds in targets.items():
                if len(preds) > 1:
                    pred = ensemble_func(preds)

                    targetLabel = QtWidgets.QLabel()
                    targetLabel.setText(target)
                    targetLabel.setAlignment(QtCore.Qt.AlignRight)
                    targetLabel.setStyleSheet("font-weight: bold")
                    targetLabel.setFixedWidth(150)

                    ensemblePredLabel = QtWidgets.QLabel()
                    ensemblePredLabel.setText(f'{pred:.3f}')
                    ensemblePredLabel.setAlignment(QtCore.Qt.AlignRight)
                    ensemblePredLabel.setFixedWidth(150)

                    self.ensembleLabels[targetLabel] = ensemblePredLabel

                    ensembleLayout = QtWidgets.QHBoxLayout()
                    ensembleLayout.addStretch()
                    ensembleLayout.addWidget(targetLabel, 0, QtCore.Qt.AlignRight)
                    ensembleLayout.addWidget(ensemblePredLabel, 0, QtCore.Qt.AlignRight)

                    self.predVBoxLayout.addLayout(ensembleLayout)
                    self.ensembleLayouts.append(ensembleLayout)

        if len(self.ensembleLayouts) == 0:
            self.ensembleLabel.setText('')

    def _remove_model(self, index):
        # remove model
        widget = self.loadedModels.pop(index)
        widget.clear_widget()
        # update index of loaded models
        for widget in self.loadedModels[index:]:
            widget.subtract_index()

        self._clear_ensemble_labels()
        # no models are loaded
        if len(self.loadedModels) == 0:
            self._clear_pred_widget()
            self.headersLayout.removeItem(self.predStretch)
            self.main_layout.addWidget(self.defaultTextLabel)
            self.main_layout.setAlignment(QtCore.Qt.AlignCenter)

    def _clear_pred_widget(self):
        self._clear_pred_headers()
        self.pred_scroll.setParent(None)

    def _clear_ensemble_labels(self):
        self.ensembleLabel.setParent(None)

        for targetLabel, predLabel in self.ensembleLabels.items():
            targetLabel.setParent(None)
            predLabel.setParent(None)
        self.ensembleLabels.clear()

        for layout in self.ensembleLayouts:
            layout.setParent(None)
        self.ensembleLayouts.clear()

    def _clear_pred_headers(self):
        self.predLabel.setParent(None)
        self.probaLabel.setParent(None)

    def update_labels(self, labels):
        for model in self.loadedModels:
            model.update_labels(labels)


class LoadedModelWidget(QtWidgets.QWidget):
    """
    Generates a widget that handles all interactions with the loaded model.

    Parameters
    ----------
    model: trained estimator

    file_name: str
        name of the loaded file

    labels: list of strings
        list of possible targets available in the loaded data

    index: int
        initial id of the model
    """

    def __init__(self, model, file_name, labels, index):
        super(LoadedModelWidget, self).__init__()

        self.model = model
        self.index = index

        self.mainHBoxLayout = QtWidgets.QHBoxLayout()
        self.mainHBoxLayout.setAlignment(QtCore.Qt.AlignBottom)

        removeButton = IdButton(self.index, '')
        removeButton.setFixedWidth(50)
        removeButton.setIcon(self.style().standardIcon(
            getattr(QtWidgets.QStyle, 'SP_DialogDiscardButton')))
        removeButton.setStatusTip('Remove model')
        self.removeButton = removeButton

        self.modelLabel = QtWidgets.QLabel()
        self.modelLabel.setText(file_name)

        self.cbTarget = QtWidgets.QComboBox()
        self.cbTarget.setFixedWidth(150)

        for target in labels:
            self.cbTarget.addItem(target)
        self.cbTarget.setCurrentIndex((len(labels) - 1))
        self.cbTarget.addItem('other')

        self.predLabel = QtWidgets.QLabel()
        self.predLabel.setText('-')
        self.predLabel.setAlignment(QtCore.Qt.AlignRight)
        self.predLabel.setFixedWidth(150)

        self.probaLabel = QtWidgets.QLabel()
        self.probaLabel.setAlignment(QtCore.Qt.AlignRight)
        self.probaLabel.setText('-')
        self.probaLabel.setFixedWidth(150)

        self.predStretch = QtWidgets.QSpacerItem(10, 0)

        self.mainHBoxLayout.addWidget(self.removeButton)
        self.mainHBoxLayout.addWidget(self.modelLabel)
        self.mainHBoxLayout.addStretch(2)
        self.mainHBoxLayout.addWidget(self.cbTarget)

        self.setLayout(self.mainHBoxLayout)

    def _prepare_data(self, df):
        # drop target column
        target = self.cbTarget.currentText()

        # don't drop any columns
        if target != 'other':
            df = df.drop(target, axis=1)

        return df.to_numpy()

    def predict(self, df):
        self._clear_prediction()

        X = self._prepare_data(df)

        # TODO: What happens if multiple rows are selected?
        # Classification
        if hasattr(self.model, 'predict_proba'):
            # mean of probabilities
            y_probas = np.max(self.model.predict_proba(X))
            proba = np.mean(np.array(y_probas))

            # majority voting
            y_preds = self.model.predict(X)
            pred = stats.mode(np.array(y_preds))[0][0]

            self.predLabel.setText(f'{pred}')
            self.probaLabel.setText(f'{proba:.3f}')

        # Regression
        if not hasattr(self.model, 'predict_proba'):
            # mean of predictions:
            y_preds = self.model.predict(X)
            pred = np.mean(np.array(y_preds))

            self.predLabel.setText(f'{pred:.3f}')

        self.mainHBoxLayout.addItem(self.predStretch)
        self.mainHBoxLayout.addWidget(self.predLabel, 0, QtCore.Qt.AlignLeft)
        self.mainHBoxLayout.addWidget(self.probaLabel, 0, QtCore.Qt.AlignLeft)

        self.setLayout(self.mainHBoxLayout)

    def subtract_index(self):
        self.index -= 1
        self.removeButton.set_id(self.index)

    def update_labels(self, labels):
        self.cbTarget.clear()

        for target in labels:
            self.cbTarget.addItem(target)
        self.cbTarget.setCurrentIndex((len(labels) - 1))
        self.cbTarget.addItem('other')

    def _clear_prediction(self):
        self.mainHBoxLayout.removeItem(self.predStretch)
        self.predLabel.setParent(None)
        self.probaLabel.setParent(None)

    def clear_widget(self):
        self.setParent(None)
