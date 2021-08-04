# importing the required libraries
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.initMenu() # TODO Menubar
        #self.initWidgets()
        # show all the widgets
        self.show()

    def initUI(self):
        # set the title
        self.setWindowTitle('Responsible Performance Prediction [Demoversion]')

        # setting  the geometry of window
        # setGeometry(left, top, width, height)
        self.setGeometry(100, 60, 1280, 720)

    def initMenu(self):
        # create actions for the menubar
        openSQLDBAction = QAction('& Load database', self)
        openSQLDBAction.setStatusTip('Opening a .sql database file.')
        openSQLDBAction.triggered.connect(self.test_action)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openSQLDBAction)

    def test_action(self):
        print('Action triggered')

    def initWidgets(self):
        # creating a label widget
        self.widget = QLabel('No database loaded.', self)


if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # start the app
    sys.exit(App.exec())
