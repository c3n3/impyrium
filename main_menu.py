import sys

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
)

import control

def sendSomething(command, args):
    print("Sent", command.name, "with", args)

def generateButtonCallbackFun(ctrl):
    def fun():
        ctrl.sendFun(ctrl, {"nothing": 0})
    return fun

def getObjectMod(ctrl):
    if ctrl.controlType == control.CONTROL_BUTTON:
        button = QPushButton()
        button.clicked.connect(generateButtonCallbackFun(ctrl))
        return button
    if ctrl.controlType == control.CONTROL_SLIDER:
        return QSlider(Qt.Orientation.Horizontal)
    return None

control.registerControl(control.Control(0, "Dumb", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb2", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb3", "nothing", control.CONTROL_BUTTON, sendSomething))
control.registerControl(control.Control(0, "Dumb4", "nothing", control.CONTROL_SLIDER, sendSomething))

_currentCategory = "nothing"
def getCurrentCategory():
    global _currentCategory
    global _currentCategory
    return _currentCategory

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impyrium")
        self.setMinimumSize(10, 10)
        widgets = [
            QComboBox,
            QDial,
            QLabel,
            QLineEdit,
            QPushButton,
            QSlider,
        ]


        container = QScrollArea()
        container.setWidgetResizable(True)
        wig = QWidget()
        wig.setMinimumSize(0, 800)
        layout = QVBoxLayout(wig)
        button = QPushButton()

        print(control.getControls())
        for c in control.getControls()[getCurrentCategory()]:
            label = QLabel(c.name)
            label.setMinimumSize(0, 100)
            mod = getObjectMod(c)
            label.setBuddy(mod)
            layout.addWidget(label)
            layout.addWidget(mod)

        wig.setLayout(layout)
        container.setWidget(wig)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(wig)

app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
