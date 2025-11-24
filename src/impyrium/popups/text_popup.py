import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QTextEdit
from PySide6.QtCore import Qt, pyqtBoundSignal, pyqtSignal, pyqtSlot, QTimer
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
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

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Return:
            self.close()

    def changeDev(self, dev):
        self.device = dev

    def popUp(self):
        super().exec()
        if self.index is not None:
            return self.items[self.index]
        return None
