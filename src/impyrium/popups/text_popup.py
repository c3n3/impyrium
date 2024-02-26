import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, pyqtBoundSignal, pyqtSignal, pyqtSlot, QTimer
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
from ..aitpi.src import aitpi
from ..aitpi_signal import AitpiSignal, AitpiSignalExecutor
import pynput
from .popup import Popup

class TextPopup(Popup):
    def __init__(self, doneFun, name, devices, parent: QWidget = None):
        super().__init__(parent)
        self.doneFun = doneFun
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.name = name
        self.devices = devices
        self.instructions.setText(name)
        self.setWindowTitle(self.name)
        self.setMinimumWidth(800)

        self.device = "All"
        self.devcombo = InputlessCombo(self)
        self.devcombo.addItem("All")
        for dev in devices:
            self.devcombo.addItem(dev)
        self.devcombo.currentIndexChanged.connect(self.changeDev)
        self.devcomboLabel = QLabel("Select Device")
        self.devcomboLabel.setBuddy(self.devcombo)

        self.mainLayout.addWidget(self.instructions)
        self.mainLayout.addWidget(self.devcomboLabel)
        self.mainLayout.addWidget(self.devcombo)

        self.text = QTextEdit(self)
        self.value = ""
        self.text.textChanged.connect(self.updateText)

        self.mainLayout.addWidget(self.text)

        self.setLayout(self.mainLayout)

    def updateText(self):
        self.value = self.text.toPlainText()
        print(self.text)

    # Required to allow us to handle on a QT thread
    def consume(self, msg):
        if msg == "CLOSE":
            self.close()

    def handleKeyEvent(self, char, event):
        if event == aitpi.BUTTON_PRESS:
            if char == pynput.keyboard.Key.enter:
                self.msgQt("CLOSE")

    def changeDev(self, dev):
        self.device = dev

    def popUp(self):
        super().exec()
        if self.index is not None:
            return self.items[self.index]
        return None

if __name__ == '__main__':
    from ..aitpi_signal import AitpiSignalExecutor
    class TestApp(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")
            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)
            self.executor = AitpiSignalExecutor()
            self.executor.start()

        def signalTimer(self):
            AitpiSignal.run()

        def addInput(self, t, item):
            print(t, item)

        def button_clicked(self, s):
            dlg = TextPopup(self.addInput, "Something", ["90", "100"], self)
            dlg.exec()

    app = QApplication(sys.argv)

    aitpi.TerminalKeyInput.startKeyListener()

    window = TestApp()
    window.show()

    app.exec()