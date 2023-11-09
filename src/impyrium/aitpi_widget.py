import sys
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtBoundSignal, QTimer, QThread, QEventLoop, pyqtSignal, QObject, pyqtSlot
import os

import aitpi
from aitpi import router

from .keycombo_dialog import KeyComboDialog
from . import control

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
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


class Selectable(QWidget):
    def __init__(self, title, items, onSelectFun, parent: QWidget = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(title)
        combo = QComboBox()
        combo.addItems(items)
        label.setBuddy(combo)
        combo.currentIndexChanged.connect(onSelectFun)
        layout.addWidget(label)
        layout.addWidget(combo)

class InputControl(QWidget, QObject):
    def __init__(self, deleteCallback, inputUnit, parent: QWidget = None):
        super().__init__(parent)
        self.deleteCallback = deleteCallback
        self.inputUnit = aitpi.InputUnit(inputUnit)
        self.startReglink = self.inputUnit['reg_link']
        self.type = self.inputUnit['type']
        if self.type == 'button':
            self.inputTrigger = self.inputUnit['trigger']
        elif self.type == 'encoder':
            self.inputTrigger = f"{self.inputUnit['left_trigger']} <-> {self.inputUnit['right_trigger']}"
        else:
            raise Exception("Invalid input unit")

        commands = aitpi.getCommands()
        topLayout = QHBoxLayout(self)
        subLayoutWidget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(self.inputTrigger)
        self.combo = QComboBox()
        self.combo.addItem('<Unset>', '')
        i = 0
        self.commands = []
        for command in commands:
            if command['input_type'] == self.type:
                self.commands.append(command)
                linkName = aitpi.InputConverter.toRegLink(command['id'], command['name'])
                self.combo.addItem(linkName)
                if linkName == self.startReglink:
                    self.combo.setCurrentIndex(i+1)
                i += 1
        label.setBuddy(self.combo)
        self.combo.currentIndexChanged.connect(self.updateInput)
        layout.addWidget(label)
        layout.addWidget(self.combo)
        subLayoutWidget.setLayout(layout)
        topLayout.addWidget(subLayoutWidget)
        delButton = QPushButton()
        delButton.setMaximumWidth(25)
        delButton.setMaximumHeight(25)
        delButton.setStyleSheet("QPushButton {background-color: darkred; color: smokewhite;}")
        delButton.setText('X')
        delButton.clicked.connect(self.deleteClicked)
        topLayout.addWidget(delButton)

    def updateInput(self, index):
        if index == 0:
            aitpi.changeInputRegLink(self.inputUnit, '', '')
            return
        index = index - 1
        aitpi.changeInputRegLink(self.inputUnit, self.commands[index]['id'], self.commands[index]['name'])

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

class Aitpi(QWidget):
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

    def addInput(self, type, triggers):
        if len(triggers) == 0:
            return
        if type == "button":
            aitpi.addInput({'trigger': triggers[0]})
            self.updateAll()
        if len(triggers) == 1:
            return
        if type == "encoder":
            aitpi.addInput({
                'left_trigger': triggers[0],
                'right_trigger': triggers[1],
                'type': 'encoder',
            })
            self.updateAll()

    def updateAll(self):
        for i in self.inputList:
            self.view.removeItem(i)
        inputs = aitpi.getInputs()
        self.inputList = [InputControl(self.inputControlDelete, x) for x in inputs]
        for i in self.inputList:
            self.view.addItem(i)
        self.update()

    def inputControlDelete(self, control):
        self.inputList.remove(control)
        self.view.removeItem(control)
        aitpi.removeInput(control.inputUnit)
        self.update()

if __name__ == "__main__":

    def run_py(message):
        print("message")
        if (message.event == aitpi.BUTTON_PRESS and message.attributes['id'] == 'python_commands'):
            os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
            print("Running file")

        if (message.event in aitpi.ENCODER_VALUES and message.attributes['id'] == 'python_encoders'):
            os.system(f"python3 {message.attributes['path']}/{message.attributes['name']} {message.event}")
            print("Running encoder")

    router.addConsumer(['python_commands', 'python_encoders'], run_py)
    aitpi.addRegistry("test_json/registry.json", "test_json/foldered_commands.json")
    aitpi.initInput("test_json/input.json")

    # aitpi.addInput('<ctrl>+9')

    # aitpi.changeInputRegLink('<ctrl>+9', 'run.py')

    # Subclass QMainWindow to customize your application's main window
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Impyrium")
            self.setMinimumSize(10, 500)
            w = Aitpi(self)
            self.setCentralWidget(w)
            self.isLinux = sys.platform.startswith('linux')

        def keyPressEvent(self, event):
            if self.isLinux:
                aitpi.pyqt6KeyPressEvent(event)

        def keyReleaseEvent(self, event):
            if self.isLinux:
                aitpi.pyqt6KeyReleaseEvent(event)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
