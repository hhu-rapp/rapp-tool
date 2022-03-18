import argparse
import os.path
import traceback
import logging
import logging
log = logging.getLogger('GUI')

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp
from rapp import gui
from rapp.gui import helper
from rapp.npipeline import Pipeline as MLPipeline
from rapp.npipeline import train_models, evaluate_fairness
from rapp.npipeline import evaluate_performance, calculate_statistics
from rapp.report.reports import save_report


class Pipeline(QtWidgets.QWidget):

    def __init__(self, qmainwindow):
        super(Pipeline, self).__init__()

        # init gui
        self.qmainwindow = qmainwindow
        self.initMLTab()

    def initMLTab(self):
        self.vlayoutMainML = QtWidgets.QVBoxLayout()
        self.gridlayoutMainML = QtWidgets.QGridLayout()
        self.menubuttonsMainML = QtWidgets.QHBoxLayout()

        self.vlayoutMainML.addLayout(self.gridlayoutMainML)
        self.vlayoutMainML.addStretch(1)
        self.vlayoutMainML.addLayout(self.menubuttonsMainML)

        # create buttons
        reportPathButton = QtWidgets.QPushButton('...')
        reportPathButton.clicked.connect(self.set_report_path)
        reportPathButton.setStatusTip('Select Report Path (Ctrl+R)')
        reportPathButton.setShortcut('Ctrl+r')
        reportPathButton.setMaximumWidth(50)

        trainButton = QtWidgets.QPushButton('Train')
        trainButton.clicked.connect(self.train)
        trainButton.setStatusTip('Train models on SQL query (Ctrl+T)')
        trainButton.setShortcut('Ctrl+t')

        # add buttons
        self.menubuttonsMainML.addWidget(trainButton)

        # labels
        self.labelName = QtWidgets.QLabel()
        self.labelName.setText('Target Variable:')

        self.labelCVariables = QtWidgets.QLabel()
        self.labelCVariables.setText('Categorical Variables:')

        self.labelSAttributes = QtWidgets.QLabel()
        self.labelSAttributes.setText('Sensitive Attributes:')

        self.labelType = QtWidgets.QLabel()
        self.labelType.setText('Type:')

        self.labelReportPath = QtWidgets.QLabel()
        self.labelReportPath.setText('Report Path:')

        self.labelImputation = QtWidgets.QLabel()
        self.labelImputation.setText('Imputation Method:')

        self.labelFSM = QtWidgets.QLabel()
        self.labelFSM.setText('Feature Selection Method:')

        self.labelEstimator = QtWidgets.QLabel()
        self.labelEstimator.setText('Estimators:')

        # create menus for configuration
        self.cbName = QtWidgets.QComboBox()
        self.leCVariables = QtWidgets.QLineEdit()
        self.cbSAttributes = helper.CheckableComboBox()
        self.cbEstimator = helper.CheckableComboBox()
        self.cbType = QtWidgets.QComboBox(self)
        self.cbType.currentIndexChanged.connect(self.update_estimators)
        self.cbType.addItem('Classification')
        self.cbType.addItem('Regression')
        self.lePath = QtWidgets.QLineEdit()
        self.lePath.setText("reports/")
        self.cbImputation = QtWidgets.QComboBox()
        self.cbImputation.addItem('Iterative')
        self.cbImputation.addItem('KNN')
        self.cbImputation.addItem('Mean')
        self.cbImputation.addItem('Median')
        self.cbImputation.addItem('Most_frequent')
        self.cbFSM = QtWidgets.QComboBox()
        self.cbFSM.addItem('Variance')

        # add labels to the grid
        self.gridlayoutMainML.addWidget(self.labelName, 0, 0)
        self.gridlayoutMainML.addWidget(self.labelCVariables, 1, 0)
        self.gridlayoutMainML.addWidget(self.labelSAttributes, 2, 0)
        self.gridlayoutMainML.addWidget(self.labelType, 3, 0)
        self.gridlayoutMainML.addWidget(self.labelReportPath, 4, 0)
        self.gridlayoutMainML.addWidget(self.labelImputation, 5, 0)
        self.gridlayoutMainML.addWidget(self.labelFSM, 6, 0)
        self.gridlayoutMainML.addWidget(self.labelEstimator, 7, 0)

        # add options to the grid
        self.gridlayoutMainML.addWidget(self.cbName, 0, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.leCVariables, 1, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.cbSAttributes, 2, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.cbType, 3, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.lePath, 4, 1)
        self.gridlayoutMainML.addWidget(self.cbImputation, 5, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.cbFSM, 6, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.cbEstimator, 7, 1, 1, -1)

        # add more options to grid
        self.gridlayoutMainML.addWidget(reportPathButton, 4, 2)

        # add to tab layout
        self.setLayout(self.vlayoutMainML)

    def refresh_labels(self):

        # refresh Target Variable comboBox
        self.cbName.clear()
        column_names = self.qmainwindow.sql_df.columns

        for feature in column_names:
            self.cbName.addItem(feature)

        self.cbName.setCurrentText(column_names[-1])

        # refresh Categorical Variable lineEdit
        self.leCVariables.clear()
        for feature in (self.qmainwindow.sql_df.select_dtypes(exclude=["number"])).columns:

            text = self.leCVariables.text()

            if text == '':
                self.leCVariables.setText(feature)
            else:
                self.leCVariables.setText(text + ',' + feature)

        self.update_estimators()
        self.update_sensitive_attributes()

    def update_sensitive_attributes(self):

        self.cbSAttributes.clear()
        for index, feature in enumerate(self.qmainwindow.sql_df.columns):
            self.cbSAttributes.addItem(feature)
            self.cbSAttributes.setItemChecked(index, checked=False)

    def update_estimators(self):

        # classifiers = ["Random Forest","Support Vector Machine","Decision Tree","Naive Bayes","Logistic Regression"]
        # reggressors = ['Elastic Net','Linear Regression','Bayesian Ridge']
        classifiers = ['RF', 'SVM', 'DT', 'NB', 'LR', 'NN']
        reggressors = ['EL', 'LR', 'BR']

        self.cbEstimator.clear()
        if self.cbType.currentText().lower() == 'classification':
            estimators = classifiers
        if self.cbType.currentText().lower() == 'regression':
            estimators = reggressors

        for index, estimator in enumerate(estimators):
            self.cbEstimator.addItem(estimator)
            self.cbEstimator.setItemChecked(index)

    def set_report_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        options |= QtWidgets.QFileDialog.ShowDirsOnly
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a Folder", "",
                                                            options=options)
        if path == '':
            path = 'reports/'

        self.lePath.setText(path)

    def train(self):
        """
        Get user input and parse to Pipeline
        Returns
        -------

        """

        cf = self.parse_settings()

        report_path = self.lePath.text()

        try:
            pl = MLPipeline(cf)

            log.info('Training models...')
            train_models(pl, cross_validation=True)

            log.info('Evaluating fairness...')
            evaluate_fairness(pl)

            log.info('Evaluating performance...')
            evaluate_performance(pl)

            log.info('Calculating statistics...')
            calculate_statistics(pl)

            log.info('Generating report...')
            save_report(pl, report_path)
            log.info('Report saved to %s',report_path)

        except Exception as e:
            log.error(traceback.format_exc())
            traceback.print_exc()

    def parse_settings(self):
        cf = argparse.Namespace()

        if self.qmainwindow.sql_df is None:
            log.error('No SQL query selected')
            return

        if len(self.cbEstimator.get_checked_items()) == 0:
            log.error('No Estimator selected')
            return

        cf.filename = None
        cf.sql_df = self.qmainwindow.sql_df
        cf.label_name = self.cbName.currentText()
        cf.categorical = self.leCVariables.text().replace(' ', '').split(',')
        cf.type = self.cbType.currentText().lower()
        cf.sensitive_attributes = self.cbSAttributes.get_checked_items()
        cf.estimators = self.cbEstimator.get_checked_items()
        cf.imputation = self.cbImputation.currentText().lower()
        cf.feature_selection = self.cbFSM.currentText().lower()

        return cf
