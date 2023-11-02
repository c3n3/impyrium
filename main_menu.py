import sys
import typing
from PyQt6 import QtCore
import device_thread
import control

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

def sendSomething(command, args):
    print("Sent", command.name, "with", args)

def generateButtonCallbackFun(ctrl):
    def fun():
        ctrl.sendFun(ctrl, {ctrl.name: 0})
    return fun

def getObjectMod(ctrl):
    if ctrl.controlType == control.CONTROL_BUTTON:
        button = QPushButton()
        button.setMinimumHeight(25)
        button.setText(ctrl.name)
        button.clicked.connect(generateButtonCallbackFun(ctrl))
        return [button]
    if ctrl.controlType == control.CONTROL_SLIDER:
        ret = QSlider(Qt.Orientation.Horizontal)
        ret.setMinimumHeight(25)
        label = QLabel(ctrl.name)
        label.setBuddy(ret)
        return [label, ret]
    return None

def init():
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
    control.registerControl(control.Control(0, "Dumb3", "Another thing", control.CONTROL_BUTTON, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Another thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Other thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Other thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Other thing", control.CONTROL_SLIDER, sendSomething))
    control.registerControl(control.Control(0, "Dumb4", "Other thing", control.CONTROL_SLIDER, sendSomething))
    control.registerDeviceType(control.DeviceType("Usb device", lambda: [control.Device(12)]))


class ControlsScrollView(QWidget):
    def __init__(self, category):
        super(ControlsScrollView, self).__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for c in control.getControls()[category]:
            mod = getObjectMod(c)
            if mod is None:
                print(f"Mod is None for {c.name}, cannot do anything with this, please fix")
                continue
            for item in mod:
                layout.addWidget(item)

        # self.setWidget(self)
        # self.setWidgetResizable(True)

class ControlsTypeSection(QWidget):
    def __init__(self, category, parent: QWidget = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        button = QPushButton(self)
        button.setText(category + " ↓")
        self.showing = False
        button.clicked.connect(self.buttonPressed)
        layout.addWidget(button)
        self.controlsView = ControlsScrollView(category)
        self.controlsView.hide()
        layout.addWidget(self.controlsView)

    def buttonPressed(self):
        self.showing = not self.showing
        print("Showing", self.showing)
        if (self.showing):
            self.controlsView.show()
        else:
            self.controlsView.hide()

class ItemScrollView(QScrollArea):
    def __init__(self, items, parent: QWidget = None) -> None:
        super(ItemScrollView, self).__init__()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for item in items:
            layout.addWidget(item)
        self.setWidget(widget)
        self.setWidgetResizable(True)

class DeviceList(QScrollArea):
    def __init__(self, parent: QWidget = None) -> None:
        super(ItemScrollView, self).__init__()
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.widget)
        self.setWidgetResizable(True)

    def newDevices(devTypes):
        for t in devTypes.keys():
            for dev in t.getVisableDevices():
                button = QPushButton()
                button.setText(dev.uid)
                self.layout.addWidget(button)


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

def run(index):
    print("Got index ", index)

class Shortcuts(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        wig = Selectable("Another", ['<ctrl->', '1', '2'], run, self)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impyrium")
        self.setMinimumSize(10, 500)
        widgets = [
            QComboBox,
            QDial,
            QLabel,
            QLineEdit,
            QPushButton,
            QSlider,
        ]

        # view = ItemScrollView(items)
        view2 = ItemScrollView([ControlsTypeSection("Other thing"), ControlsTypeSection("nothing"), ControlsTypeSection("Another thing")])
        layout = QHBoxLayout()
        tabwidget = QTabWidget()

        tabwidget.addTab(Shortcuts(), "Section 1")
        tabwidget.addTab(view2, "Section 2")
        layout.addWidget(ItemScrollView([]))

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(tabwidget)

device_thread.start()

init()

app = QApplication(sys.argv)

window = MainWindow()
window.show()


app.exec()
