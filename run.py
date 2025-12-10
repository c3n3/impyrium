import py_global_shortcuts as pygs

PYGS_APPNAME = "impyrium_app"

if __name__ == "__main__":
    pygs.binding_handle(PYGS_APPNAME)

import time
from src import impyrium
from src.impyrium.widgets.main_impyrium import DeviceList
from src.impyrium import control
from src.impyrium.main_menu import SuperWindow
from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QHBoxLayout
from src.impyrium import common_css
from src.impyrium import main_menu
from src.impyrium.widgets import main_impyrium

def detect():
    return [control.Device(0, "Usb device")]

def reserve(device):
    return

def release(device):
    return


def otherDevices():
    ret = []
    for i in range(2):
        ret.append(control.Device(f"{i} Other", "Other device"))
    return ret

pygs.init(PYGS_APPNAME, cache_dir="./temp")
impyrium.init("./temp", "./test_json/registry.json", "./test_json/folder_commands.json")

# Add all controls and devices

def doSomething(ctrl: control.Control, event, devlist: list[control.Device]):
    print("Got", ctrl.name, "with", event, devlist)

control.registerControl(control.ControlSelector("Selector", "Selector0", doSomething, ["1", "2", "3"]))
control.registerControl(control.ControlButton("Category1", "Control1", doSomething))
control.registerControl(control.ControlButton("Category1", "Control2", doSomething))
control.registerControl(control.ControlButton("Category1", "Control3", doSomething))
control.registerControl(control.ControlFile("Category1", "File", doSomething))
control.registerControl(control.ControlButton("Category2", "Control4", doSomething))
control.registerControl(control.ControlSlider("Category2", "Control5", doSomething, sliderRange=control.RangeValue(0, 100, 0.5)))
control.registerControl(control.ControlSlider("Category2", "Control6", doSomething, sliderRange=control.RangeValue(0, 100, 0.5)))
control.registerControl(control.ControlSlider("Category3", "Control7", doSomething, sliderRange=control.RangeValue(-100, 100, 0.5)))
control.registerControl(control.ControlSlider("Category3", "Control8", doSomething, sliderRange=control.RangeValue(0, 100, 0.5)))

usbDevices = control.DeviceType(
    "Usb device",
    detector=detect,
    releaseDeviceFun=release,
    reserveDeviceFun=reserve,
    autoReservationTimeout=5,
    controlCategories=["Category1"]
)

otherDevs = control.DeviceType(
    "Other device",
    detector=otherDevices,
    controlCategories=["Category3"]
)

control.registerDeviceType(usbDevices)
control.registerDeviceType(otherDevs)

def filterDev(dev: control.Device):
    # Filter out devices that are not of type "Usb device"
    return dev.deviceType.name != "Usb device"

class DataInputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.deviceList = DeviceList(self, filter=filterDev)
        # Create a horizontal layout to split device list (left) and inputs (right)
        main_layout = QHBoxLayout()
        layout.addLayout(main_layout)

        # Device list on the left
        main_layout.addWidget(self.deviceList)

        # Right side: input fields and data display
        right_side = QVBoxLayout()

        # Input fields
        input_layout = QHBoxLayout()
        self.input1 = QLineEdit()
        self.input1.setPlaceholderText("Input 1")
        self.input2 = QLineEdit()
        self.input2.setPlaceholderText("Input 2")
        input_layout.addWidget(self.input1)
        input_layout.addWidget(self.input2)
        right_side.addLayout(input_layout)

        # Big textbox for displaying data
        self.data_display = QTextEdit()
        self.data_display.setPlaceholderText("Data display")
        self.data_display.setMinimumHeight(200)
        right_side.addWidget(self.data_display)

        # Set stretch factors: right_side takes 2, deviceList takes 1
        main_layout.setStretchFactor(self.deviceList, 1)
        main_layout.addLayout(right_side)
        main_layout.setStretchFactor(right_side, 2)
        main_layout.addLayout(right_side)

        self.setLayout(layout)

class MainWindow(SuperWindow):
    def __init__(self):
        super().__init__()

    def setMainImpyrium(self, mainImpyrium: QWidget):
        self.setWindowTitle("Test Super Window")
        self.layoutWidget = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # Data input tab
        data_input_tab = DataInputTab()

        self.tabs.setStyleSheet(common_css.TAB_STYLE)

        self.mainImpyrium = mainImpyrium
        self.mainImpyrium.setParent(self)

        self.tabs.addTab(self.mainImpyrium, "Impyrium")
        self.tabs.addTab(data_input_tab, "Data Input")

        self.setLayout(self.layoutWidget)
        self.layoutWidget.addWidget(self.tabs)

import sys

app = QApplication(sys.argv)

try:
    impyrium.start()
    main_window = MainWindow()
    main_men = main_menu.MainWindow(logo=None, title="Impyrium Test", superWindow=main_window)
    main_men.show()
    app.exec()
finally:
    pygs.deinit()
