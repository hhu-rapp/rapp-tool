import time
import logging
log = logging.getLogger('GUI')

from PyQt5 import QtWidgets, QtGui, QtCore


class Color(QtWidgets.QWidget):
    # Works as a placeholder
    def __init__(self, color, label_str='Label'):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        # background color
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))

        # label
        label = QtWidgets.QLabel()
        label.setText(label_str)
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(label, 0, 0)

        # self.setLayout(layout)
        self.setPalette(palette)


class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()
        self._changed = False
        self.view().pressed.connect(self.handle_item_pressed)

    def setItemChecked(self, index, checked=True):

        item = self.model().item(index, self.modelColumn())  # QStandardItem object

        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def find_item_index(self, text):
        item = self.model().findItems(text)
        item_index = self.model().indexFromItem(item[0])
        return item_index.row()

    def handle_item_pressed(self, index):

        item = self.model().itemFromIndex(index)
        self._changed = True

        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def hidePopup(self):

        if not self._changed:
            super().hidePopup()
        self._changed = False

    def _item_checked(self, index):
        item = self.model().item(index)
        return item.checkState() == QtCore.Qt.Checked

    def get_checked_items(self):
        items = []
        for i in range(super().count()):
            if self._item_checked(i):
                items.append(super().itemText(i))

        return items

    def check_items(self, options):

        for index in range(super().count()):
            item = self.model().item(index)
            item.setCheckState(QtCore.Qt.Unchecked)

        for option in options:
            option = option.replace("'", "")
            item = self.model().findItems(option)

            if len(item) == 0:
                log.error(f'Could not find Item: {option}')
                continue

            item[0].setCheckState(QtCore.Qt.Checked)


class LoggingHandler(logging.Handler):

    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.parent = parent

    def emit(self, record):
        self.parent.write(self.format(record))


class LoggingTextBrowser(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.textBrowser = QtWidgets.QTextBrowser(self)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        vbox.addWidget(self.textBrowser)

    def write(self, s):
        self.textBrowser.append(s)


class LoadModelPushButton(QtWidgets.QPushButton):

    def __init__(self, id):
        """
        A QPushButton with an id.

        Parameters
        ----------
        id: int
            id to be passed to clicked.connect method.
        """
        super().__init__('...')
        self.id = id

        super().setStatusTip('Load Model')
        super().setMaximumWidth(50)

    def set_click_function(self, function):
        super().clicked.connect(lambda: function(self.id))


class ClickableLabel(QtWidgets.QLabel):

    def __init__(self, index):
        """
        A QLabel with an id.

        Parameters
        ----------
        id: int
            id to be passed to clicked.connect method.
        """
        super().__init__()
        self.mouseReleaseEvent = super().mouseReleaseEvent
        self.id = index

    def set_click_function(self, function):
        self.mouseReleaseEvent = (lambda i: function(self.id))
