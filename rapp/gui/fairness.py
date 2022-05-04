import argparse
import os.path

# PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets

# rapp gui
from rapp import gui
from rapp.gui.pipeline import Pipeline


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
		self.individual_tab.setLayout(QtWidgets.QGridLayout())
		
		# add to layout
		self.tabs.addTab(self.individual_tab, 'Individual Model')
