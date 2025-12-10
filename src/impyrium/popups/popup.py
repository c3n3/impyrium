import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget
from PySide6.QtCore import Qt, QTimer
from .. import helpers
from .. import work_queue

class Popup(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        QTimer.singleShot(1,self.focusAndShowWindow)
        self.executor = work_queue.WorkQueueExecutor()
        self.executor.start()

    def focusAndShowWindow(self):
        self.setMinimumWidth(100)
        if self.windowState() != Qt.WindowState.WindowMaximized:
            if not helpers.isWayland():
                self.showMaximized()
            self.showNormal()
        else:
            self.showNormal()
            if not helpers.isWayland():
                self.showMaximized()
        self.raise_()
        self.activateWindow()

    def end(self):
        self.executor.stop()

    def popUp(self):
        return super().exec()

    def closeEvent(self, event):
        self.end()
        event.accept()

    def close(self):
        self.end()
        super().close()
