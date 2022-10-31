import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from scipy.stats import stats

from rapp.gui.helper import IdButton
from rapp.pipeline import preprocess_data


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

        self.predStretch = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum,
                                                 QtWidgets.QSizePolicy.Expanding)

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

        X = preprocess_data(df, df.select_dtypes(exclude=["number"]).columns)

        return X

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
