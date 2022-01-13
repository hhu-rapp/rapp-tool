import time

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
            item = self.model().findItems(option)

            if len(item) == 0:
                print(f"Could not find Item: {option}")
                continue

            item[0].setCheckState(QtCore.Qt.Checked)


def timeLogMsg(msg):
    """

    Parameters
    ----------
    msg: str

    Returns
    -------
    out: str
        log call with time
    """
    timestr = time.asctime(time.localtime(time.time()))
    return '[' + timestr + '] ' + msg
