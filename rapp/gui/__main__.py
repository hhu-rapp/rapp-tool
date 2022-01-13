import sys

from PyQt5.QtWidgets import QApplication

from rapp.gui import Window

if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
    App.setStyle("Fusion")

    # create the instance of our Window
    window = Window()

    # run
    window.show()
    sys.exit(App.exec())
