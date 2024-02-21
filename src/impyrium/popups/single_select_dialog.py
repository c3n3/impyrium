import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal, pyqtSlot, QTimer
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
from ..aitpi.src import aitpi
from ..aitpi_signal import AitpiSignal, AitpiSignalExecutor
import pynput

class SingleSelectDialog(QDialog):
    def __init__(self, doneFun, name, items, devices, parent: QWidget = None):
        super().__init__(parent)
        self.doneFun = doneFun
        self.msgId = "SINGLE_SELECT_DIALOG"
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.name = name
        self.devices = devices
        self.instructions.setText(name)
        self.setWindowTitle(self.name)
        self.setMinimumWidth(450)

        self.signalExecutor = AitpiSignalExecutor()
        self.signalExecutor.start()

        aitpi.registerKeyHandler(self.handleKeyEvent)

        self.index = None

        self.devcombo = InputlessCombo(self)
        self.items = items
        for item in self.items:
            self.devcombo.addItem(item)
        self.devcombo.currentIndexChanged.connect(self.changeType)
        self.devcomboLabel = QLabel("Select Device")
        self.devcomboLabel.setBuddy(self.devcombo)

        self.mainLayout.addWidget(self.instructions)
        self.mainLayout.addWidget(self.devcomboLabel)
        self.mainLayout.addWidget(self.devcombo)

        aitpi.router.addConsumer([self.msgId], self)

        selectionItems = []
        idx = 0
        for item in self.items:
            button = QPushButton(self)
            button.setMinimumHeight(25)
            button.setText(item)
            button.pressed.connect(self.generateButtonCallbackFun(idx))
            idx += 1
            selectionItems.append(button)

        self.selection = ItemScrollView(selectionItems)

        self.items = items
        self.mainLayout.addWidget(self.selection)

        self.setLayout(self.mainLayout)

    # Required to allow us to handle on a QT thread
    def consume(self, msg):
        event, value = msg
        if event == "CLOSE":
            self.index = value
            self.close()
        else:
            self.setIndex(value)

    def handleKeyEvent(self, char, event):
        if event == aitpi.BUTTON_PRESS:
            if char == pynput.keyboard.Key.down: #event.key() == 0x01000013: # Up
                idx = None
                if self.index is None:
                    idx = 0
                else:
                    idx = (self.index + 1) % len(self.items)
                AitpiSignal.send(self.msgId, ("INDEX", idx))
            elif char == pynput.keyboard.Key.up:
                idx = None
                if self.index is None:
                    idx = 0
                else:
                    idx = self.index - 1
                    if idx < 0:
                        idx = len(self.items) - 1
                AitpiSignal.send(self.msgId, ("INDEX", idx))
            elif char == pynput.keyboard.Key.enter: # event.key() == 0x01000004 or event.key() == 0x01000005: # Enter or return
                AitpiSignal.send(self.msgId, ("CLOSE", self.index))

    def setIndex(self, idx):
        if idx == self.index:
            self.selection.toggleIndexHighlight(self.index)
            self.index = None
        elif idx != self.index:
            if self.index is not None:
                self.selection.toggleIndexHighlight(self.index)
            self.index = idx
            self.selection.toggleIndexHighlight(self.index)

    def generateButtonCallbackFun(self, index):
        def fun():
            self.setIndex(index)
            self.update()
        return fun

    def changeType(self, index):
        print(index)
        self.update()

    def popUp(self):
        super().exec()
        if self.index is not None:
            return self.items[self.index]
        return None

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

if __name__ == '__main__':
    class TestApp(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")
            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)
            self.timer=QTimer()
            self.timer.timeout.connect(self.signalTimer)
            self.timer.setInterval(100)
            self.timer.start()

        def signalTimer(self):
            AitpiSignal.run()

        def addInput(self, t, item):
            print(t, item)

        def button_clicked(self, s):
            dlg = SingleSelectDialog(self.addInput, "Something", ["one", "two"], ["90", "100"], self)
            dlg.exec()

    app = QApplication(sys.argv)

    aitpi.TerminalKeyInput.startKeyListener()

    window = TestApp()
    window.show()

    app.exec()