import argparse
import traceback
import logging
import logging
import time

from pandas.core.dtypes.common import is_numeric_dtype

log = logging.getLogger('GUI')

# PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer

# rapp
from rapp import gui
from rapp import models
from rapp.gui import helper
from rapp.pipeline import Pipeline as MLPipeline
from rapp.pipeline import train_models, evaluate_fairness
from rapp.pipeline import evaluate_performance, calculate_statistics
from rapp.report import save_report


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
        self.reportPathButton = reportPathButton

        trainButton = QtWidgets.QPushButton('Train')
        trainButton.clicked.connect(self.train)
        trainButton.setStatusTip('Train models on SQL query (Ctrl+T)')
        trainButton.setShortcut('Ctrl+t')
        trainButton.setEnabled(False)
        self.trainButton = trainButton

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

        # self.labelImputation = QtWidgets.QLabel()
        # self.labelImputation.setText('Imputation Method:')
        #
        # self.labelFSM = QtWidgets.QLabel()
        # self.labelFSM.setText('Feature Selection Method:')

        self.labelEstimator = QtWidgets.QLabel()
        self.labelEstimator.setText('Estimators:')

        # create menus for configuration
        self.cbName = QtWidgets.QComboBox()
        self.cbName.currentIndexChanged.connect(self.update_type)
        self.leCVariables = QtWidgets.QLineEdit()
        self.cbSAttributes = helper.CheckableComboBox()
        self.cbEstimator = helper.CheckableComboBox()
        self.cbType = QtWidgets.QComboBox(self)
        self.cbType.currentIndexChanged.connect(self.update_estimators)
        self.cbType.addItem('Classification')
        self.cbType.addItem('Regression')
        self.lePath = QtWidgets.QLineEdit()
        self.lePath.setText("reports/")
        # self.cbImputation = QtWidgets.QComboBox()
        # self.cbImputation.addItem('Iterative')
        # self.cbImputation.addItem('KNN')
        # self.cbImputation.addItem('Mean')
        # self.cbImputation.addItem('Median')
        # self.cbImputation.addItem('Most_frequent')
        # self.cbFSM = QtWidgets.QComboBox()
        # self.cbFSM.addItem('Variance')

        # add labels to the grid
        self.gridlayoutMainML.addWidget(self.labelName, 0, 0)
        self.gridlayoutMainML.addWidget(self.labelCVariables, 1, 0)
        self.gridlayoutMainML.addWidget(self.labelSAttributes, 2, 0)
        self.gridlayoutMainML.addWidget(self.labelType, 3, 0)
        self.gridlayoutMainML.addWidget(self.labelReportPath, 4, 0)
        # self.gridlayoutMainML.addWidget(self.labelImputation, 5, 0)
        # self.gridlayoutMainML.addWidget(self.labelFSM, 6, 0)
        self.gridlayoutMainML.addWidget(self.labelEstimator, 7, 0)

        # add options to the grid
        self.gridlayoutMainML.addWidget(self.cbName, 0, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.leCVariables, 1, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.cbSAttributes, 2, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.cbType, 3, 1, 1, -1)
        self.gridlayoutMainML.addWidget(self.lePath, 4, 1)
        # self.gridlayoutMainML.addWidget(self.cbImputation, 5, 1, 1, -1)
        # self.gridlayoutMainML.addWidget(self.cbFSM, 6, 1, 1, -1)
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
        self.leCVariables.setText(', '.join((self.qmainwindow.sql_df.select_dtypes(exclude=["number"])).columns))

        self.update_estimators()
        self.update_sensitive_attributes()
        self.update_type()

    def update_sensitive_attributes(self):
        self.cbSAttributes.clear()
        for index, feature in enumerate(self.qmainwindow.sql_df.columns):
            self.cbSAttributes.addItem(feature)
            self.cbSAttributes.setItemChecked(index, checked=False)

            if feature == "Deutsch" or feature == "Geschlecht":
                self.cbSAttributes.setItemChecked(index, checked=True)

    def update_estimators(self):
        classifiers = models.models['classification'].keys()
        regressors = models.models['regression'].keys()

        self.cbEstimator.clear()
        if self.cbType.currentText().lower() == 'classification':
            estimators = classifiers
        if self.cbType.currentText().lower() == 'regression':
            estimators = regressors

        for index, estimator in enumerate(estimators):
            self.cbEstimator.addItem(estimator)
            self.cbEstimator.setItemChecked(index)

    def update_type(self):
        # set type depending on number of unique values of the last column
        if self.cbName.currentText() not in self.qmainwindow.sql_df.columns:
            return
        else:
            if is_numeric_dtype(self.qmainwindow.sql_df[self.cbName.currentText()]):
               if any((self.qmainwindow.sql_df[self.cbName.currentText()] % 1) > 0):
                   self.cbType.setCurrentText("Regression")
               else:
                   self.cbType.setCurrentText("Classification")
            else:
                self.cbType.setCurrentText("Classification")

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
        Trains the ML pipeline from given user input in separate thread.
        """
        self.cf = self.parse_settings()

        if self.cf is None:
            return



        self.trainbtn_thread = QThread()
        self.trainbtn_worker = TrainButtonUpdater(self.trainButton)
        self.trainbtn_worker.moveToThread(self.trainbtn_thread)

        self.trainbtn_thread.started.connect(self.trainbtn_worker.run)


        self.training_thread = QThread()
        self.worker = Trainer(self, self.cf)

        self.worker.moveToThread(self.training_thread)

        self.training_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.trainbtn_worker.interrupt)
        self.worker.finished.connect(self.trainbtn_thread.quit)
        self.worker.finished.connect(self.training_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.trainbtn_worker.deleteLater)
        self.training_thread.finished.connect(self.training_thread.deleteLater)
        self.trainbtn_thread.finished.connect(self.trainbtn_thread.deleteLater)

        self.worker.success.connect(self._setup_tabs_after_training)

        self.trainbtn_thread.start()
        self.training_thread.start()



    def _setup_tabs_after_training(self, pl: MLPipeline):
        cf = self.cf
        # Enable Tab to save models
        self.qmainwindow.settings.tab.setTabEnabled(self.qmainwindow.settings.individual_tab_idx, True)

        if pl.fairness_results[next(iter(pl.fairness_results))]:
            data_settings = {"studies_id": getattr(cf, "studies_id", None),
                             "features_id": getattr(cf, "features_id", None),
                             "labels_id": getattr(cf, "labels_id", None)}

            # Enable Evaluation tab
            self.qmainwindow.tabs.setTabEnabled(self.qmainwindow.evaluation_tab_index, True)
            self.qmainwindow.tabs.widget(self.qmainwindow.evaluation_tab_index).populate_tabs(pl,
                                                                                              data_settings)
            self.qmainwindow.settings.refresh_data(pl, data_settings)
        else:
            self.qmainwindow.tabs.setTabEnabled(self.qmainwindow.evaluation_tab_index, False)
            log.warning("No sensitive attributes selected, fairness evaluation was skipped.")

        # Enable Interpretability tab
        self.qmainwindow.tabs.setTabEnabled(self.qmainwindow.interpretability_tab_index, True)
        self.qmainwindow.tabs.widget(self.qmainwindow.interpretability_tab_index).initialize_tab(pl)



    def parse_settings(self):
        cf = argparse.Namespace()

        if self.qmainwindow.sql_df is None:
            log.error('No SQL query selected')
            return None

        if len(self.cbEstimator.get_checked_items()) == 0:
            log.error('No Estimator selected')
            return None

        cf.filename = None

        if self.qmainwindow.databaseLayoutWidget.features_id is not None:
            studies_feat_id = self.qmainwindow.databaseLayoutWidget.features_id.split('_', 1)
            cf.studies_id = studies_feat_id[0]
            cf.features_id = studies_feat_id[1]
        if self.qmainwindow.databaseLayoutWidget.labels_id is not None:
            cf.labels_id = self.qmainwindow.databaseLayoutWidget.labels_id

        cf.sql_df = self.qmainwindow.databaseLayoutWidget.sql_df
        cf.label_name = self.cbName.currentText()
        cf.categorical = self.leCVariables.text().replace(' ', '').split(',')
        cf.type = self.cbType.currentText().lower()
        cf.sensitive_attributes = self.cbSAttributes.get_checked_items()
        cf.estimators = self.cbEstimator.get_checked_items()

        return cf


class Trainer(QObject):
    finished = pyqtSignal()
    success = pyqtSignal(MLPipeline)

    def __init__(self, app: Pipeline, cf):
        super().__init__()
        self.caller = app
        self.cf = cf

    def run(self):
        try:
            report_path = self.caller.lePath.text()

            pl = MLPipeline(self.cf)

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
            log.info('Report saved to %s', report_path)

        except Exception as e:
            log.error(traceback.format_exc())
            traceback.print_exc()
            self.finished.emit()
            return

        self.finished.emit()
        self.success.emit(pl)


class TrainButtonUpdater(QObject):

    def __init__(self, btn):
        super().__init__()
        self.btn = btn
        self.old_text = self.btn.text()


        self.animation = ["", ".", "..", "..."]
        self.anim_step = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

    def run(self):
        self.btn.setEnabled(False)
        self.update()
        self.timer.start(500)

    def update(self):
        self.btn.setText("Training" + self.animation[self.anim_step])
        self.anim_step = (self.anim_step + 1) % len(self.animation)


    def interrupt(self):
        self.timer.stop()
        self.btn.setText(self.old_text)
        self.btn.setEnabled(True)
