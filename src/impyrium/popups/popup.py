import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal, pyqtSlot, QTimer
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
from ..aitpi.src import aitpi
from ..aitpi_signal import AitpiSignal, AitpiSignalExecutor
import pynput

class Popup(QDialog):
    popupCount = 0

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.signalExecutor = AitpiSignalExecutor()
        self.signalExecutor.start()
        aitpi.registerKeyHandler(self.handleKeyEvent)
        self.id = Popup.popupCount
        Popup.popupCount += 1
        self.msgId = f"POPUP_{self.id}"
        aitpi.router.addConsumer([self.msgId], self)

    # Required to allow us to handle on a QT thread
    def consume(self, msg):
        # Derived class should override
        pass

    def msgQt(self, msg):
        AitpiSignal.send(self.msgId, msg)

    def handleKeyEvent(self, char, event):
        pass

    def popUp(self):
        return super().exec()

    def end(self):
        aitpi.removeKeyHandler(self.handleKeyEvent)
        aitpi.router.removeConsumer([self.msgId], self)
        self.signalExecutor.stop()

    def closeEvent(self, event):
        self.end()
        event.accept()

    def close(self):
        self.end()
        super().close()
