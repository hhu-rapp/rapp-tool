import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp
from rapp import gui
from rapp.pipeline import MLPipeline


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
        trainButton = QtWidgets.QPushButton('Train')
        trainButton.clicked.connect(self.train)

        validateButton = QtWidgets.QPushButton('Validate')
        validateButton.clicked.connect(self.validate)

        # add buttons
        self.menubuttonsMainML.addWidget(trainButton)
        self.menubuttonsMainML.addWidget(validateButton)

        # labels
        self.labelName = QtWidgets.QLabel()
        self.labelName.setText('Target Variable:')

        self.labelCVariables = QtWidgets.QLabel()
        self.labelCVariables.setText('Categorical Variables:')

        self.labelType = QtWidgets.QLabel()
        self.labelType.setText('Type:')

        self.labelReportPath = QtWidgets.QLabel()
        self.labelReportPath.setText('Report Path:')

        self.labelImputation = QtWidgets.QLabel()
        self.labelImputation.setText('Imputation Method:')

        self.labelFSM = QtWidgets.QLabel()
        self.labelFSM.setText('Feature Selection Method:')

        # create menus for configuration
        self.leName = QtWidgets.QLineEdit()
        self.leCVariables = QtWidgets.QLineEdit()
        self.cbType = QtWidgets.QComboBox()
        self.cbType.addItem('Classification')
        self.cbType.addItem('Regression')
        self.lePath = QtWidgets.QLineEdit()
        self.cbImputation = QtWidgets.QComboBox()
        self.cbImputation.addItem('Iterative')
        self.cbFSM = QtWidgets.QComboBox()
        self.cbFSM.addItem('Variance')

        # add labels to the grid
        self.gridlayoutMainML.addWidget(self.labelName, 0, 0)
        self.gridlayoutMainML.addWidget(self.labelCVariables, 1, 0)
        self.gridlayoutMainML.addWidget(self.labelType, 2, 0)
        self.gridlayoutMainML.addWidget(self.labelReportPath, 3, 0)
        self.gridlayoutMainML.addWidget(self.labelImputation, 4, 0)
        self.gridlayoutMainML.addWidget(self.labelFSM, 5, 0)

        # add options to the grid
        self.gridlayoutMainML.addWidget(self.leName, 0, 1)
        self.gridlayoutMainML.addWidget(self.leCVariables, 1, 1)
        self.gridlayoutMainML.addWidget(self.cbType, 2, 1)
        self.gridlayoutMainML.addWidget(self.lePath, 3, 1)
        self.gridlayoutMainML.addWidget(self.cbImputation, 4, 1)
        self.gridlayoutMainML.addWidget(self.cbFSM, 5, 1)

        # add to tab layout
        self.setLayout(self.vlayoutMainML)

    def train(self):
        """
        Get user input and parse to MLPipeline
        Returns
        -------

        """

        args = argparse.Namespace()

        if self.qmainwindow.sql_df is None:
            msg = gui.helper.timeLogMsg('No SQL query to train from')
            self.qmainwindow.loggingTextBrowser.append(msg)
            return

        args.sql_df = self.qmainwindow.sql_df
        args.label_name = self.leName.text()
        args.categorical = self.leCVariables.text().replace(' ', '').split(',')
        args.type = self.cbType.currentText().lower()
        args.imputation = self.cbImputation.currentText().lower()
        args.feature_selection = self.cbFSM.currentText().lower()
        args.plot_confusion_matrix = 'True'
        args.report_path = ''
        args.save_report = 'True'
        args.sensitive_attributes = []
        args.classifier = None

        try:
            MLPipeline(args)
        except Exception as e:
            msg = gui.helper.timeLogMsg(str(e))
            self.qmainwindow.loggingTextBrowser.append(msg)

            # print("Error in SQL code:", e)

        MLPipeline(args)



    def validate(self):
        pass