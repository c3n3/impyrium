from . import signals
from . import work_queue

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QScrollArea
)

import time
import io
from datetime import datetime

class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        # adding label to the layout
        lay.addWidget(self.label)

    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)

class TextDisplay(QWidget):
    _textDisplays: list["TextDisplay"] = []
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.label = ScrollLabel(self)
        self.box = QVBoxLayout(self)
        self.box.addWidget(self.label)
        self.setLayout(self.box)
        self.setMinimumSize(250, 10)
        self.msgs = []
        self.startTime = time.time()
        TextDisplay._textDisplays.append(self)

    def addMessage(self, msg):
        if len(self.msgs) > 100:
            self.msgs.pop(0)
        self.msgs.append(msg)

        self.updateText()

    def updateText(self):
        text = ""
        for time, timeString, item in reversed(self.msgs):
            text += f"{timeString} - {item}"

        self.label.setText(text)

        self.update()
        self.label.update()

    @staticmethod
    def print(*args, **kwargs):
        import io
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()

        now = datetime.now()
        timeString = now.strftime("%H:%M:%S")

        send = (time.time(), timeString, contents)

        def updateAllDisplays(message):
            for disp in TextDisplay._textDisplays:
                disp.addMessage(message)

        work_queue.schedule(lambda: updateAllDisplays(send))
