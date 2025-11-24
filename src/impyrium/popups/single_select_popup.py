import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QSpacerItem
from PySide6.QtCore import QTimer
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
import pynput
from .popup import Popup
from .. import common_css
from ..widgets.custom_button import ImpPushButton
from PySide6.QtCore import Qt

class SingleSelectPopup(Popup):
    def __init__(self, doneFun, name, items, devices, parent: QWidget = None):
        super().__init__(parent)
        self.doneFun = doneFun
        self.setStyleSheet(common_css.MAIN_STYLE)
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.name = name
        if len(devices) == 1:
            self.devices = list(devices)
        else:
            self.devices = ["All", *devices]
        self.instructions.setText(name)
        self.setWindowTitle(self.name)
        self.setMinimumWidth(450)

        self.devIndex = 0
        self.index = None
        self.devcombo = InputlessCombo(self)
        self.items = items
        for dev in self.devices:
            if type(dev) is str:
                self.devcombo.addItem(dev)
            else:
                self.devcombo.addItem(dev.getName())
        self.devcombo.currentIndexChanged.connect(self.changeType)
        self.devcomboLabel = QLabel("Select Device")
        self.devcomboLabel.setBuddy(self.devcombo)

        self.mainLayout.addWidget(self.instructions)
        self.mainLayout.addWidget(self.devcomboLabel)
        self.mainLayout.addWidget(self.devcombo)

        selectionItems = []
        idx = 0
        for item in self.items:
            button = ImpPushButton(self)
            button.setMinimumHeight(25)
            button.setText(item)
            button.clicked.connect(self.generateButtonCallbackFun(idx))
            idx += 1
            selectionItems.append(button)

        self.selection = ItemScrollView(selectionItems)

        self.items = items
        self.mainLayout.addWidget(self.selection)
        button = ImpPushButton(self)
        button.setText("Done")
        button.clicked.connect(lambda: self.close())
        self.mainLayout.addWidget(button)
        self.setLayout(self.mainLayout)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Down:
            idx = None
            if self.index is None:
                idx = 0
            else:
                idx = (self.index + 1) % len(self.items)
            self.setIndex(idx)
        elif key == Qt.Key.Key_Up:
            idx = None
            if self.index is None:
                idx = 0
            else:
                idx = self.index - 1
                if idx < 0:
                    idx = len(self.items) - 1
            self.setIndex(idx)
        elif key == Qt.Key.Key_Return:
            self.close()

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
        self.devIndex = index
        self.update()

    def popUp(self):
        super().exec()
        dev = []
        if self.devices[self.devIndex] == "All":
            dev = self.devices[1:]
        else:
            dev = [self.devices[self.devIndex]]

        if self.index is not None:
            return dev, self.items[self.index]
        return dev, None
