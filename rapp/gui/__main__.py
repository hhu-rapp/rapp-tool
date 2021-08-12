import sys

from PyQt5.QtWidgets import QApplication

from rapp.gui import Window


if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = Window()

    # start the app
    sys.exit(App.exec())
