# PyQt5
import joblib
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox

from rapp.gui.helper import CheckableComboBox, ClickableLabel
from rapp.util import estimator_name

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

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
		self.tabs.addTab(self.overview_tab, 'Model Summary')

	def __init_individual_tab(self):
		# create layout
		self.individual_tab = QtWidgets.QWidget()
		self.individual_tab.setLayout(QtWidgets.QVBoxLayout())

		# add to layout
		tab_idx = self.tabs.addTab(self.individual_tab, 'Model Inspection')
		self.individual_tab_idx = tab_idx

	def populate_fairness_tabs(self, pipeline, data_settings):
		"""
		Parameters
		----------
		pipeline: rapp.pipeline object
			A pipeline object with trained models.

		It is expected that the object has following attributes:
		data, sensitive_attributes, score_functions, statistics_results,
		fairness_functions, performance_results, fairness_results, type.

		data_settings: dict
			It represents the loaded data in the pipeline, it has the form:
			{'studies_id': studies_id of train data,
			'features_id': features_id of train data,
			'labels_id': predicting label_id of the model}
		"""
		self.pipeline = pipeline
		self.data_settings = data_settings

		self.refresh_tabs()
		self.populate_dataset_tab()
		self.populate_overview_tab()
		self.populate_individual_tab()

	def populate_dataset_tab(self):
		pl_type = self.pipeline.type

		if pl_type == "classification":
			self.populate_dataset_table()
		if pl_type == "regression":
			self.populate_dataset_plot()

	def populate_dataset_plot(self):
		# one groupBox per sensitive attribute
		for i, sensitive in enumerate(self.pipeline.sensitive_attributes):
			sensitiveHBoxLayout = QtWidgets.QHBoxLayout()
			self.sensitiveGroupBox.append(QGroupBox(sensitive.capitalize()))
			self.sensitiveGroupBox[i].setLayout(sensitiveHBoxLayout)
			# one groupBox per mode
			groupbox = []
			for j, mode in enumerate(self.pipeline.data):
				groupbox.append(QGroupBox(mode.capitalize()))
				vBoxLayout = QtWidgets.QVBoxLayout()
				groupbox[j].setLayout(vBoxLayout)

				# add fig canvas to groupBox
				fig, ax = plt.subplots(figsize=(5, 3))
				plotCanvas = FigureCanvas(fig)
				vBoxLayout.addWidget(plotCanvas, alignment=Qt.AlignCenter)

				# plot subgroups outcomes
				subgroups = list(self.pipeline.statistics_results[mode]['groups'][sensitive].keys())
				for k, subgroup in enumerate(subgroups):
					outcomes = self.pipeline.statistics_results[mode]['groups'][sensitive][subgroup]['outcomes']
					ax.hist(outcomes, label=str(subgroup), density=True, histtype="step")

					plt.legend()
					plt.xlabel(self.data_settings['labels_id'])
					plt.ylabel('Density')
					fig.tight_layout()

				plotCanvas.draw()

				sensitiveHBoxLayout.addWidget(groupbox[j])
			# add to layout
			self.dataset_tab.layout().addWidget(self.sensitiveGroupBox[i])


	def populate_dataset_table(self):
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
		pl_type = self.pipeline.type.capitalize()
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
		overviewTopLayout.addRow(f"{pl_type} Metrics:", self.cbPerformance)
		overviewTopLayout.addRow('Fairness Metrics:', self.cbFairness)
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
		pl_type = self.pipeline.type

		# create groupBox
		self.overview_groupBox = QGroupBox(f"{str(mode).capitalize()} - {sensitive}:")
		self.overview_groupBox.setFlat(True)
		self.overview_groupBox.setStyleSheet("border:0;")
		tableGridLayout = QtWidgets.QGridLayout()
		self.overview_groupBox.setLayout(tableGridLayout)

		# model labels
		for i, model in enumerate(models):
			labelModel = ClickableLabel(i)
			labelModel.set_click_function(self.open_individual_tab)
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
					if pl_type == "classification":
						# average value across sensitive attribute
						measure = np.zeros(len(values))
						for k, value in enumerate(values):
							measure[k] = values[value]['affected_percent']

						measure = np.mean(measure)

					if pl_type == "regression":
							measure = values

					labelValue = QtWidgets.QLabel()
					labelValue.setText(f"{measure:.3f}")
					tableGridLayout.addWidget(labelValue, i + 1, j + 1)

		# add to layout
		self.overview_tab.layout().addWidget(self.overview_groupBox)

	def populate_individual_tab(self):
		# comboBox for filtering
		self.cbModels = QtWidgets.QComboBox()
		self.individual_cbMetrics = QtWidgets.QComboBox()

		# groupBox for the filters
		self.individual_metrics_groupBox = QGroupBox("Filters")
		individualTopLayout = QtWidgets.QFormLayout()
		self.individual_metrics_groupBox.setLayout(individualTopLayout)

		# load comboBoxes
		for model in self.pipeline.performance_results:
			self.cbModels.addItem(estimator_name(model))
		self.individual_cbMetrics.addItem("Performance")
		self.individual_cbMetrics.addItem("Fairness")

		self.individual_cbMetrics.currentIndexChanged.connect(self.populate_individual_table)
		self.cbModels.currentIndexChanged.connect(self.populate_individual_table)

		# add to groupBox
		individualTopLayout.addRow('Model:', self.cbModels)
		individualTopLayout.addRow('Metrics:', self.individual_cbMetrics)

		# add to layout
		self.individual_tab.layout().addWidget(self.individual_metrics_groupBox)
		self.populate_individual_table()

	def populate_individual_table(self):
		self.clear_individual_table()
		# get values from filters
		metric_type = self.individual_cbMetrics.currentText()

		model_idx = self.cbModels.currentIndex()
		models = list(self.pipeline.performance_results.keys())
		model = models[model_idx]

		pl_type = self.pipeline.type
		if metric_type == "Performance":
			# one groupBox per mode
			for i, mode in enumerate(self.pipeline.data):
				self.individual_mode_groupBox.append(QGroupBox(mode.capitalize()))
				tableGridLayout = QtWidgets.QGridLayout()
				self.individual_mode_groupBox[i].setLayout(tableGridLayout)

				# performance metrics labels
				metrics = self.pipeline.performance_results[model][mode]['scores']
				for j, metric in enumerate(metrics):
					labelMetric = QtWidgets.QLabel()
					labelMetric.setText(str(metric).capitalize())
					labelMetric.setStyleSheet("font-weight: bold")
					tableGridLayout.addWidget(labelMetric, j, 0, alignment=Qt.AlignCenter)
					# performance measures
					value = metrics[metric]
					labelValue = QtWidgets.QLabel()
					labelValue.setText(f"{value:.3f}")
					tableGridLayout.addWidget(labelValue, j, 1, alignment=Qt.AlignCenter)

				# add to layout
				self.individual_tab.layout().addWidget(self.individual_mode_groupBox[i])

		if metric_type == "Fairness":
			# one groupBox per mode
			for i, mode in enumerate(self.pipeline.data):
				self.individual_mode_groupBox.append(QGroupBox(mode.capitalize()))
				tableGridLayout = QtWidgets.QGridLayout()
				self.individual_mode_groupBox[i].setLayout(tableGridLayout)
				# cumulative offset for the sensitive attributes labels
				cum_offset = 0

				for j, sensitive in enumerate(self.pipeline.sensitive_attributes):
					metrics = self.pipeline.fairness_results[model][sensitive]

					if pl_type == "classification":
						for k, metric in enumerate(self.pipeline.fairness_results[model][sensitive]):
							# fairness metrics labels
							labelMetric = QtWidgets.QLabel()
							labelMetric.setText(str(metric).capitalize())
							labelMetric.setStyleSheet("font-weight: bold")
							tableGridLayout.addWidget(labelMetric, k + 2, 0)

							values = metrics[metric][mode]
							# offset for group title
							offset = len(values)

							for l, value in enumerate(values):
								measure = values[value]['affected_percent']
								# subgroup labels
								labelSubgroup = QtWidgets.QLabel()
								labelSubgroup.setText(str(value).capitalize())
								tableGridLayout.addWidget(labelSubgroup, 1, l + cum_offset + 1)
								# fairness measures labels
								labelValue = QtWidgets.QLabel()
								labelValue.setText(f"{measure:.3f}")
								tableGridLayout.addWidget(labelValue, k+2, l + cum_offset + 1)

						# group labels
						labelGroup = QtWidgets.QLabel()
						labelGroup.setText(str(sensitive).capitalize())
						labelGroup.setStyleSheet("font-weight: bold")
						tableGridLayout.addWidget(labelGroup, 0, j + cum_offset, 1, offset, alignment=Qt.AlignCenter)

						cum_offset += offset

					if pl_type == "regression":
						for k, metric in enumerate(self.pipeline.fairness_results[model][sensitive]):
							# fairness metrics labels
							labelMetric = QtWidgets.QLabel()
							labelMetric.setText(str(metric).capitalize())
							labelMetric.setStyleSheet("font-weight: bold")
							tableGridLayout.addWidget(labelMetric, k + 1, 0, alignment=Qt.AlignCenter)

							measure = metrics[metric][mode]
							# fairness measures labels
							labelValue = QtWidgets.QLabel()
							labelValue.setText(f"{measure:.3f}")
							tableGridLayout.addWidget(labelValue, k + 1, j+1, alignment=Qt.AlignCenter)

						# group labels
						labelGroup = QtWidgets.QLabel()
						labelGroup.setText(str(sensitive).capitalize())
						labelGroup.setStyleSheet("font-weight: bold")
						tableGridLayout.addWidget(labelGroup, 0, j+1, alignment=Qt.AlignCenter)

				# add to layout
				self.individual_tab.layout().addWidget(self.individual_mode_groupBox[i])

	def clear_individual_table(self):
		try:
			for widget in self.individual_mode_groupBox:
				widget.setParent(None)
			self.individual_mode_groupBox = []
			self.individual_groupBox.setParent(None)
		except AttributeError:
			return

	def refresh_tabs(self):
		try:
			self.individual_metrics_groupBox.setParent(None)
			self.overview_metrics_groupBox.setParent(None)
		except AttributeError:
			return

		self.clear_dataset_table()
		self.clear_overview_table()
		self.clear_individual_table()

	def open_individual_tab(self, model_index):
		self.tabs.setCurrentIndex(self.individual_tab_idx)
		self.cbModels.setCurrentIndex(model_index)
