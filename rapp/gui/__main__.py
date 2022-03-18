import sys
import logging

from PyQt5.QtWidgets import QApplication

from rapp.gui import Window

log = logging.getLogger('GUI')
log.setLevel(logging.INFO)
log_pipeline = logging.getLogger("rapp.pipeline")
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(filename)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler('rapp.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
log.addHandler(file_handler)
log_pipeline.addHandler(file_handler)

if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)
    App.setStyle("Fusion")

    # create the instance of our Window
    window = Window()

    # run
    window.show()
    sys.exit(App.exec())
