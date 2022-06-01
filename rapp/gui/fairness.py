# PyQt5
import joblib
from PyQt5 import QtCore, QtGui, QtWidgets

from rapp.util import estimator_name


class FairnessWidget(QtWidgets.QWidget):
	
	def __init__(self, qmainwindow):
		super(FairnessWidget, self).__init__()
		
		self.qmainwindow = qmainwindow
	
	def initUI(self, pipeline, data_settings):
		"""
		Parameters
		----------
		pipeline: rapp.pipeline object
		    A pipeline object with trained models.
		    
		data_settings: a dict with the features and labels of the train data, with the form of:
			{'studies_id': studies_id of train data,
        	'features_id': features_id of train data,
        	'labels_id': predicting label_id of the model}
		"""
		# create layout
		layout = QtWidgets.QHBoxLayout()
		layout.setContentsMargins(0, 10, 0, 0)
		self.setLayout(layout)
		
		# create widgets
		self.tabs = QtWidgets.QTabWidget()
		
		self.pipeline = pipeline
		self.data_settings = data_settings
		self.__init_dataset_tab()
		self.__init_overview_tab()
		self.__init_individual_tab()
		
		# add widgets to layout
		layout.addWidget(self.tabs)
	
	def __init_dataset_tab(self):
		self.dataset_tab = QtWidgets.QWidget()
		self.dataset_tab.setLayout(QtWidgets.QGridLayout())
		
		# add to layout
		self.tabs.addTab(self.dataset_tab, 'Dataset')
	
	def __init_overview_tab(self):
		self.overview_tab = QtWidgets.QWidget()
		self.overview_tab.setLayout(QtWidgets.QGridLayout())
		
		# add to layout
		self.tabs.addTab(self.overview_tab, 'Model Overview')
	
	def __init_individual_tab(self):
		self.individual_tab = QtWidgets.QWidget()
		self.individual_tab.setLayout(QtWidgets.QVBoxLayout())
		self.topLayout = QtWidgets.QHBoxLayout()
		self.topLayout.setContentsMargins(11, 11, 11, 0)
		
		labelModels = QtWidgets.QLabel()
		labelModels.setText("Model: ")
		self.cbModels = QtWidgets.QComboBox(
		
		)
		self.cbModels.clear()
		
		for model in self.pipeline.fairness_results:
		
			self.cbModels.addItem(estimator_name(model))
		
		# add to layout
		self.topLayout.addWidget(labelModels)
		self.topLayout.addWidget(self.cbModels)
		
		self.individual_tab.layout().addLayout(self.topLayout)
		
		# sensitive labels
		for sensitive in self.pipeline.sensitive_attributes:
			sensitiveLayout = QtWidgets.QGridLayout()
			labelSensitive = QtWidgets.QLabel()
			labelSensitive.setText(sensitive)
			
			# mode labels
			for i, mode in enumerate(self.pipeline.data):
				labelMode = QtWidgets.QLabel()
				labelMode.setText(mode.capitalize())
				labelMode.setStyleSheet("font-weight: bold")
				
				sensitiveLayout.addWidget(labelMode, 0, i)
			
			# add to layout
			self.individual_tab.layout().addWidget(labelSensitive)
			self.individual_tab.layout().addLayout(sensitiveLayout)

		tab_idx = self.tabs.addTab(self.individual_tab, 'Individual Model')
		self.individual_tab_idx = tab_idx
