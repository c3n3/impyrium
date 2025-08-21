import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QWidget
from PySide6.QtCore import Qt, QTimer
from ..aitpi.src import aitpi
from ..aitpi_signal import AitpiSignal, AitpiSignalExecutor

class Popup(QDialog):
    popupCount = 0

    def __init__(self, parent: QWidget = None, executor=True):
        super().__init__(parent)
        if executor:
            self.signalExecutor = AitpiSignalExecutor()
            self.signalExecutor.start()
        else:
            self.signalExecutor = None
        aitpi.registerKeyHandler(self.handleKeyEvent)

        # A slight hack, but we provide an interface to msg the QT thread
        # We could potentially create a new system for this
        self.id = Popup.popupCount
        Popup.popupCount += 1
        self.msgId = f"POPUP_{self.id}"
        aitpi.router.addConsumer([self.msgId], self)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        QTimer.singleShot(1,self.focusAndShowWindow)

    def focusAndShowWindow(self):
        if self.windowState() != Qt.WindowState.WindowMaximized:
            self.showMaximized()
            self.showNormal()
        else:
            self.showNormal()
            self.showMaximized()

        self.raise_()
        self.activateWindow()

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
        if self.signalExecutor is not None:
            self.signalExecutor.stop()

    def closeEvent(self, event):
        self.end()
        event.accept()

    def close(self):
        self.end()
        super().close()
