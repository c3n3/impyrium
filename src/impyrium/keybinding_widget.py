import sys
import PySide6
from PySide6 import QtCore
from PySide6.QtCore import QObject
import os

import py_global_shortcuts as pygs

from .widgets.custom_button import ImpPushButton

from .keycombo_dialog import KeyComboDialog
from . import control
from . import helpers

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
)

class ScrollPassCombo(QComboBox):
    def __init__(self, scrollWidget=None, *args, **kwargs):
        super(ScrollPassCombo, self).__init__(*args, **kwargs)
        self.scrollWidget=scrollWidget

    def wheelEvent(self, *args, **kwargs):
        return self.scrollWidget.wheelEvent(*args, **kwargs)

class InputControl(QWidget, QObject):
    def __init__(self, deleteCallback, shortcut, scrollWidget, parent: QWidget = None):
        super().__init__(parent)
        self.scrollWidget = scrollWidget
        self.deleteCallback = deleteCallback
        self.shortcut = shortcut
        self.startReglink = "No Reg Link"
        self.type = "No Type"

        commands = pygs.get_binder().get_commands()
        self.binding = pygs.get_binder().get_key_binding(self.shortcut)
        topLayout = QHBoxLayout(self)
        subLayoutWidget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(self.shortcut)
        self.combo = ScrollPassCombo(scrollWidget)
        self.combo.view().setAutoScroll(False)
        self.combo.addItem('<Unset>', '')
        i = 0
        self.commands: list[pygs.Command] = []
        for command in commands:
            self.commands.append(command)
            self.combo.addItem(command.name)
            if self.binding is not None and self.binding.has_command(command.cmd_id):
                self.combo.setCurrentIndex(i+1)
            i += 1
        label.setBuddy(self.combo)
        self.combo.currentIndexChanged.connect(self.updateInput)
        layout.addWidget(label)
        layout.addWidget(self.combo)
        subLayoutWidget.setLayout(layout)
        topLayout.addWidget(subLayoutWidget)
        delButton = ImpPushButton()
        delButton.setMaximumWidth(25)
        delButton.setMaximumHeight(25)
        delButton.setIcon(QtGui.QIcon(helpers.getImageForPyQt("cancel_button")))
        delButton.setIconSize(PySide6.QtCore.QSize(25,25))
        delButton.clicked.connect(self.deleteClicked)
        topLayout.addWidget(delButton)
        self.current_command_id = None

    def updateInput(self, index):
        if index == 0:
            pygs.get_binder().unlink_command(self.shortcut, self.commands[index].cmd_id)
            return
        index = index - 1
        binder = pygs.get_binder()
        binder.unlink_command(self.shortcut, self.current_command_id)
        binder.link_command(self.shortcut, self.commands[index].cmd_id)
        self.current_command_id = self.commands[index].cmd_id

    def deleteClicked(self):
        self.deleteCallback(self)

class ItemScrollView(QScrollArea):
    def __init__(self, items, parent: QWidget = None) -> None:
        super(ItemScrollView, self).__init__(parent)
        widget = QWidget()
        self.mainLayout = QVBoxLayout(widget)
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for item in items:
            self.mainLayout.addWidget(item)
        self.setWidget(widget)
        self.setWidgetResizable(True)

    def addItem(self, item):
        self.mainLayout.addWidget(item)

    def removeItem(self, item):
        self.mainLayout.removeWidget(item)

class KeybindingWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.inputList = []
        self.view = ItemScrollView(self.inputList)
        self.mainlayout = QVBoxLayout()
        addInputButton = QPushButton()
        addInputButton.setText("Click to add input")
        addInputButton.clicked.connect(self.runInputDialog)
        self.mainlayout.addWidget(addInputButton)
        self.mainlayout.addWidget(self.view)

        self.setLayout(self.mainlayout)
        self.updateAll()

    def runInputDialog(self):
        dlg = KeyComboDialog(self.addInput)
        dlg.exec()

    def addInput(self, shortcut):
        if shortcut == "":
            return
        binder = pygs.get_binder()
        binder.create_key_binding(shortcut)
        self.updateAll()

    def updateAll(self):
        for i in self.inputList:
            self.view.removeItem(i)
        binder = pygs.get_binder()
        inputs = binder.get_key_bindings()
        self.inputList = [InputControl(self.inputControlDelete, x.shortcut, self.view) for x in inputs]
        for i in self.inputList:
            self.view.addItem(i)
        self.update()

    def inputControlDelete(self, control: InputControl):
        if control not in self.inputList:
            return
        self.inputList.remove(control)
        self.view.removeItem(control)
        binder = pygs.get_binder()
        binder.delete_key_binding(control.shortcut)
        self.updateAll()
        control.deleteLater()

