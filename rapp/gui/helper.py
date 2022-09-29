import re
import time
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor

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


class IdButton(QtWidgets.QPushButton):

    def __init__(self, id, text='...'):
        """
        A QPushButton with an id.

        Parameters
        ----------
        id: int
            id to be passed to clicked.connect method.
        """
        super().__init__(text)
        self.id = id

    def set_click_function(self, function):
        self.clicked.connect(lambda: function(self.id))


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


class CollapsibleBox(QtWidgets.QWidget):
    """
    Collapsible Box widget
    Code from:
    https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt
    """

    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QtWidgets.QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        vBoxLayout = QtWidgets.QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.addWidget(self.toggle_button)
        vBoxLayout.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        self.content_area.setLayout(layout)
        collapsed_height = (
                self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount() - 1):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(100)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1)
        content_animation.setDuration(100)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}

    def add_mapping(self, pattern, pattern_format):
        self._mapping[pattern] = pattern_format

    def highlightBlock(self, text_block):
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)


def init_sql_highlighter(highlighter, sql_field):

    # SQL operations
    sql_format = QTextCharFormat()
    sql_format.setForeground(QColor("#2088b5"))
    pattern = r'SELECT|FROM|WHERE|JOIN|INNER |OUTER |LEFT |RIGHT |CASE WHEN |THEN | END| AS |GROUP BY | ON |IF |ELSE '
    highlighter.add_mapping(pattern, sql_format)
    pattern = r'select | from | where | join | inner | outer | left | right | case when | then | end | as | group by ' \
              r'| on | if | else'
    highlighter.add_mapping(pattern, sql_format)

    # Numbers
    number_format = QTextCharFormat()
    number_format.setForeground(QColor("#9a0357"))
    pattern = r'[0-9]| null| NULL| [0-9]\.[0-9]'
    highlighter.add_mapping(pattern, number_format)

    # Logic operations
    logic_format = QTextCharFormat()
    logic_format.setForeground(QColor("#a67f5a"))
    pattern = r'and |or |in |is |AND |OR |IN |IS |not |NOT ||> |<| |= |\+|\*|\/' \
              r'|exists |EXISTS |like |LIKE |glob |GLOB | is null| IS NULL| unique| UNIQUE'
    highlighter.add_mapping(pattern, logic_format)

    # Aggregate functions
    aggregate_format = QTextCharFormat()
    aggregate_format.setForeground(QColor("#845ec2"))
    pattern = r'avg()|AVG()|count()|COUNT()|min()|MIN()|max()|MAX()|sum()|SUM()|total()|TOTAL()'
    highlighter.add_mapping(pattern, aggregate_format)

    # Comparison
    compare_format = QTextCharFormat()
    compare_format.setForeground(QColor("#a67f5a"))
    pattern = r'==|!=|<>|>|<|>=|<=|!<|!>'
    highlighter.add_mapping(pattern, compare_format)

    # Strings
    string_format = QTextCharFormat()
    string_format.setForeground(QColor("#81ab2d"))
    pattern = r'"(.*?)"|strftime()'
    highlighter.add_mapping(pattern, string_format)

    # Comments
    comment_format = QTextCharFormat()
    comment_format.setForeground(QColor("#73777B"))
    comment_format.setFontItalic(True)
    pattern = r'--.*$'
    highlighter.add_mapping(pattern, comment_format)

    highlighter.setDocument(sql_field.document())
