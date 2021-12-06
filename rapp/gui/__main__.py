import sys

from PyQt5.QtWidgets import QApplication

from rapp.gui import Window
import PyQt5

if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
    App.setStyle("Fusion")
    print(PyQt5.QtWidgets.QStyleFactory.keys())
    # create the instance of our Window
    window = Window()

    # run
    window.show()
    sys.exit(App.exec())
