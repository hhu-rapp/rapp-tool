# PyQt5
import joblib
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.helper import CheckableComboBox
from rapp.util import estimator_name


class FairnessWidget(QtWidgets.QWidget):
	
	def __init__(self, qmainwindow):
		super(FairnessWidget, self).__init__()
		
		self.qmainwindow = qmainwindow
		self.initUI()
	
	def initUI(self):
		# create layout
		layout = QtWidgets.QHBoxLayout()
		layout.setContentsMargins(0, 10, 0, 0)
		self.setLayout(layout)
		
		# create widgets
		self.tabs = QtWidgets.QTabWidget()
		
		self.sensitiveGroupBox = []
		self.individual_mode_groupBox = []
		
		self.__init_dataset_tab()
		self.__init_overview_tab()
		self.__init_individual_tab()
		
		# add widgets to layout
		layout.addWidget(self.tabs)
	
	def __init_dataset_tab(self):
		# create layout
		self.dataset_tab = QtWidgets.QWidget()
		self.dataset_tab.setLayout(QtWidgets.QVBoxLayout())
		
		# add to layout
		self.tabs.addTab(self.dataset_tab, 'Dataset')
	
	def __init_overview_tab(self):
		# create layout
		self.overview_tab = QtWidgets.QWidget()
		self.overview_tab.setLayout(QtWidgets.QVBoxLayout())
		
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
		
	def populate_fairness_tabs(self, pipeline):
		"""
		Parameters
		----------
		pipeline: rapp.pipeline object
		    A pipeline object with trained models.

		It is expected that the object has following attributes:
		data, sensitive_attributes, score_functions, statistics_results,
		fairness_functions, performance_results, fairness_results
		"""
		self.pipeline = pipeline

		self.refresh_tabs()
		self.populate_dataset_tab()
		self.populate_overview_tab()

	def populate_dataset_tab(self):	
		# one groupBox per sensitive attribute
		for i, sensitive in enumerate(self.pipeline.sensitive_attributes):
			sensitiveHBoxLayout = QtWidgets.QHBoxLayout()
			self.sensitiveGroupBox.append(QGroupBox(sensitive.capitalize()))
			self.sensitiveGroupBox[i].setLayout(sensitiveHBoxLayout)

			# one groupBox per mode
			groupbox = []
			for j, mode in enumerate(self.pipeline.data):
				groupbox.append(QGroupBox(mode.capitalize()))
				tableGridLayout = QtWidgets.QGridLayout()
				groupbox[j].setLayout(tableGridLayout)

				# 'Class' label
				labelClass = QtWidgets.QLabel()
				labelClass.setText("Class")
				labelClass.setStyleSheet("font-weight: bold")
				tableGridLayout.addWidget(labelClass, 0, 0)

				# subgroups labels
				subgroups = list(self.pipeline.statistics_results[mode]['groups'][sensitive].keys())
				for k, subgroup in enumerate(subgroups):
					labelSubgroup = QtWidgets.QLabel()
					labelSubgroup.setText(str(subgroup).capitalize())
					labelSubgroup.setStyleSheet("font-weight: bold")
					tableGridLayout.addWidget(labelSubgroup, 0, k + 1)

					# classes labels
					classes = list(self.pipeline.statistics_results[mode]['outcomes'].keys())
					for l, class_name in enumerate(classes):
						labelClass = QtWidgets.QLabel()
						labelClass.setText(str(class_name).capitalize())
						labelClass.setStyleSheet("font-weight: bold")
						tableGridLayout.addWidget(labelClass, l + 1, 0)

						# value labels
						value = self.pipeline.statistics_results[mode]['groups'][sensitive][subgroup]['outcomes'][
							class_name]
						labelValue = QtWidgets.QLabel()
						labelValue.setText(str(value))
						tableGridLayout.addWidget(labelValue, l + 1, k + 1)

						# class total labels
						total_class = self.pipeline.statistics_results[mode]['outcomes'][class_name]
						labelClasstotal = QtWidgets.QLabel()
						labelClasstotal.setText(str(total_class))
						tableGridLayout.addWidget(labelClasstotal, l + 1, len(subgroups) + 1)

					# subgroups total labels
					total_subgroup = self.pipeline.statistics_results[mode]['groups'][sensitive][subgroup]['total']
					labelSubtotal = QtWidgets.QLabel()
					labelSubtotal.setText(str(total_subgroup))
					tableGridLayout.addWidget(labelSubtotal, len(classes) + 1, k + 1)

				# total labels
				labelTotal = QtWidgets.QLabel()
				labelTotal.setText("Total")
				labelTotal.setStyleSheet("font-weight: bold")
				tableGridLayout.addWidget(labelTotal, 0, len(subgroups) + 1)

				labelTotal2 = QtWidgets.QLabel()
				labelTotal2.setText("Total")
				labelTotal2.setStyleSheet("font-weight: bold")
				tableGridLayout.addWidget(labelTotal2, len(classes) + 1, 0)

				# total outcomes label
				total_samples = self.pipeline.statistics_results[mode]['total']
				labelSampleTotal = QtWidgets.QLabel()
				labelSampleTotal.setText(str(total_samples))
				tableGridLayout.addWidget(labelSampleTotal, len(classes) + 1, len(subgroups) + 1)

				sensitiveHBoxLayout.addWidget(groupbox[j])
			# add to layout
			self.dataset_tab.layout().addWidget(self.sensitiveGroupBox[i])

	def clear_dataset_table(self):
		for widget in self.sensitiveGroupBox:
			widget.setParent(None)
		self.sensitiveGroupBox = []

	def populate_overview_tab(self):
		# comboBox for filtering
		self.cbPerformance = CheckableComboBox()
		self.cbFairness = CheckableComboBox()
		self.cbOverviewModes = QtWidgets.QComboBox()
		self.cbSenstitiveAttributes = QtWidgets.QComboBox()

		# groupBox for the filters
		self.overview_metrics_groupBox = QGroupBox("Filters")
		self.overview_metrics_groupBox.size()
		overviewTopLayout = QtWidgets.QFormLayout()
		self.overview_metrics_groupBox.setLayout(overviewTopLayout)

		# load comboBoxes
		performance_metrics = list(self.pipeline.score_functions.keys())
		for metric in performance_metrics:
			self.cbPerformance.addItem(str(metric))
		self.cbPerformance.check_items(performance_metrics)

		fairness_notions = list(self.pipeline.fairness_functions.keys())
		for notion in fairness_notions:
			self.cbFairness.addItem(str(notion))
		self.cbFairness.check_items(fairness_notions)

		modes = list(self.pipeline.data.keys())
		for mode in modes:
			self.cbOverviewModes.addItem(str(mode).capitalize())

		for sensitive in self.pipeline.sensitive_attributes:
			self.cbSenstitiveAttributes.addItem(str(sensitive).capitalize())

		self.cbPerformance.currentIndexChanged.connect(self.populate_overview_table)
		self.cbFairness.currentIndexChanged.connect(self.populate_overview_table)
		self.cbOverviewModes.currentIndexChanged.connect(self.populate_overview_table)
		self.cbSenstitiveAttributes.currentIndexChanged.connect(self.populate_overview_table)

		# add to groupBox
		overviewTopLayout.addRow('Performance:', self.cbPerformance)
		overviewTopLayout.addRow('Fairness:', self.cbFairness)
		overviewTopLayout.addRow('Mode:', self.cbOverviewModes)
		overviewTopLayout.addRow('Sensitive Attribute:', self.cbSenstitiveAttributes)

		# add to layout
		self.overview_tab.layout().addWidget(self.overview_metrics_groupBox)
		self.populate_overview_table()

	def clear_overview_table(self):
		try:
			self.overview_groupBox.setParent(None)
		except AttributeError:
			return

	def populate_overview_table(self):
		self.clear_overview_table()
		# get values from filters
		mode = self.cbOverviewModes.currentText().lower()
		sensitive = self.cbSenstitiveAttributes.currentText()
		performance_metrics = self.cbPerformance.get_checked_items()
		fairness_notions = self.cbFairness.get_checked_items()
		metrics = self.cbPerformance.get_checked_items()
		metrics.extend(fairness_notions)

		models = list(self.pipeline.performance_results.keys())

		# create groupBox
		self.overview_groupBox = QGroupBox(f"{str(mode).capitalize()} - {sensitive}:")
		self.overview_groupBox.setFlat(True)
		self.overview_groupBox.setStyleSheet("border:0;")
		tableGridLayout = QtWidgets.QGridLayout()
		self.overview_groupBox.setLayout(tableGridLayout)

		# model labels
		for i, model in enumerate(models):
			labelModel = QtWidgets.QLabel()
			labelModel.setText(estimator_name(model))
			labelModel.setStyleSheet("font-weight: bold")
			tableGridLayout.addWidget(labelModel, i+1, 0)

			# metrics labels
			for j, metric in enumerate(metrics):
				labelMetric = QtWidgets.QLabel()
				labelMetric.setText(str(metric))
				labelMetric.setStyleSheet("font-weight: bold")
				tableGridLayout.addWidget(labelMetric, 0, j+1)

				if metric in performance_metrics:
					# performance metrics
					value = self.pipeline.performance_results[model][mode]['scores'][metric]
					labelValue = QtWidgets.QLabel()
					labelValue.setText(f"{value:.3f}")
					tableGridLayout.addWidget(labelValue, i+1, j+1)

				if metric in fairness_notions:
					# fairness notions
					values = self.pipeline.fairness_results[model][sensitive][metric][mode]
					# average value per sensitive attribute
					measure = np.zeros(len(values))
					for k, value in enumerate(values):
						measure[k] = values[value]['affected_percent']
					avg_measure = np.mean(measure)
					labelValue = QtWidgets.QLabel()
					labelValue.setText(f"{avg_measure:.3f}")
					tableGridLayout.addWidget(labelValue, i + 1, j + 1)

		# add to layout
		self.overview_tab.layout().addWidget(self.overview_groupBox)
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
	def refresh_tabs(self):
		try:
			self.overview_metrics_groupBox.setParent(None)
		except AttributeError:
			return

		self.clear_dataset_table()
		self.clear_overview_table()
