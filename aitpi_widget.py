import sys
import typing
from PyQt6 import QtCore
import device_thread
import os
import control
import time
from aitpi.src import aitpi
from aitpi.src.aitpi import router
import threading

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

class ButtonInputControl(QWidget):
    def __init__(self, inputUnit, parent: QWidget = None):
        super(ButtonInputControl, self).__init__(parent)
        self.startReglink = inputUnit['reg_link']
        self.inputTrigger = inputUnit['trigger']
        self.commands = aitpi.getCommands()
        print(self.commands)
        layout = QVBoxLayout(self)
        label = QLabel(self.inputTrigger)
        self.combo = QComboBox()
        self.combo.addItem('<Unset>', '')
        i = 0
        for command in self.commands:
            linkName = aitpi.InputConverter.toRegLink(command['id'], command['name'])
            self.combo.addItem(linkName)
            if linkName == self.startReglink:
                self.combo.setCurrentIndex(i+1)
            i += 1
        self.combo.setCurrentIndex
        label.setBuddy(self.combo)
        self.combo.currentIndexChanged.connect(self.updateInput)
        layout.addWidget(label)
        layout.addWidget(self.combo)

    def updateInput(self, index):
        print(index)
        if index == 0:
            aitpi.changeInputRegLink(self.inputTrigger, '', '')
            return
        index = index - 1
        aitpi.changeInputRegLink(self.inputTrigger, self.commands[index]['id'], self.commands[index]['name'])

class ItemScrollView(QScrollArea):
    def __init__(self, items, parent: QWidget = None) -> None:
        super(ItemScrollView, self).__init__(parent)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for item in items:
            layout.addWidget(item)
        self.setWidget(widget)
        self.setWidgetResizable(True)

class Aitpi(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        inputs = aitpi.getInputs()
        inputList = [ButtonInputControl(x) for x in inputs]
        view2 = ItemScrollView(inputList)
        layout = QVBoxLayout()
        layout.addWidget(view2)

        self.setLayout(layout)

if __name__ == "__main__":

    def run_py(message):
        if (message.event == aitpi.BUTTON_PRESS and message.attributes['id'] == 'python_commands'):
            os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
            print("Running file")

    router.addConsumer(['python_commands'], run_py)
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

    print("Trying to run pyqt6")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
