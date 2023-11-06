import sys
import typing
from PyQt6 import QtCore
import device_thread
import control
import time
from aitpi.src import aitpi
from aitpi.src.aitpi import router

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
    def __init__(self, inputTrigger, parent: QWidget = None):
        super(ButtonInputControl, self).__init__(parent)
        self.inputTrigger = inputTrigger
        self.commands = aitpi.getCommands()
        print(self.commands)
        layout = QVBoxLayout(self)
        label = QLabel(inputTrigger)
        self.combo = QComboBox()
        self.combo.addItems(["sdf", '1'])
        label.setBuddy(self.combo)
        self.combo.currentIndexChanged.connect(self.updateInput)
        layout.addWidget(label)
        layout.addWidget(self.combo)

    def updateInput(self, index):
        aitpi.changeInputRegLink(self.inputTrigger, None)

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

        view2 = ItemScrollView([QLabel("Hellow"), QLabel("Hellow2"), ButtonInputControl("<ctrl>+5")])
        layout = QVBoxLayout()
        layout.addWidget(view2)

        self.setLayout(layout)


if __name__ == "__main__":

    def run_py(message):
        if (message.event == aitpi.BUTTON_PRESS and message.attributes['type'] == 'python_commands'):
            os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
            print("Running file")

    router.addConsumer([1], run_py)
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

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()