import sys
import time

from .aitpi.src.aitpi import router
from .aitpi.src import aitpi

from .aitpi_widget import Aitpi
from . import device_thread
from . import control
from .worker_thread import WorkerThread

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
    QHBoxLayout,
)

def printAllOfType(item, t):
    for d in dir(item):
        if (type(item.__getattribute__(d)) == t):
            print(d)

class ControlsScrollView(QWidget):
    def __init__(self, category):
        super(ControlsScrollView, self).__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controls = control.getControls()
        self.worker = WorkerThread()
        self.worker.start()
        if category in controls:
            for c in controls[category]:
                mod = self.getObjectMod(c)
                if mod is None:
                    print(f"Mod is None for {c.name}, cannot do anything with this, please fix")
                    continue
                for item in mod:
                    layout.addWidget(item)

    def generateButtonCallbackFun(self, ctrl):
        def fun():
            ctrl.sendFun(ctrl, aitpi.BUTTON_PRESS, control.DeviceType.getControlDevList(ctrl))
        return fun

    def generateSliderCallbackFun(self, ctrl):
        def fun(value):
            item = lambda: ctrl.sendFun(ctrl,
                                        control.ControlEvents.VALUE_SET,
                                        control.DeviceType.getControlDevList(ctrl),
                                        arguments={"value": ctrl.controlType.convertSliderValue(value)})
            if 'event' in ctrl.data and ctrl.data['event'] is not None:
                self.worker.removeItem(ctrl.data['event'])
            ctrl.data['event'] = self.worker.scheduleItem(0.5, item)
        return fun

    def getObjectMod(self, ctrl):
        if type(ctrl.controlType) == control.ControlButton:
            button = QPushButton()
            button.setMinimumHeight(25)
            button.setText(ctrl.name)
            button.released.connect(self.generateButtonCallbackFun(ctrl))
            return [button]
        if type(ctrl.controlType) == control.ControlSlider:
            ret = QSlider(Qt.Orientation.Horizontal)
            res = ctrl.controlType.generateSliderValues()
            ret.setMinimum(res[0])
            ret.setMaximum(res[1])
            ret.setMinimumHeight(25)
            label = QLabel(ctrl.name)
            ret.valueChanged.connect(self.generateSliderCallbackFun(ctrl))
            label.setBuddy(ret)
            return [label, ret]
        return None

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
        if (self.showing):
            self.controlsView.show()
        else:
            self.controlsView.hide()

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

class DeviceList(QScrollArea):
    def __init__(self, parent: QWidget = None, selectDeviceFun = None) -> None:
        super(DeviceList, self).__init__(parent)
        self.widg = QWidget()
        self.box = QVBoxLayout(self.widg)
        self.box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.widg)
        self.setWidgetResizable(True)
        self.objectNameChanged.connect(self.newDevices)
        self.widgetList = []
        self.selectedDevice = None
        self.selectedDeviceWidget = None
        self.selectDeviceFun = selectDeviceFun

    def selectDevice(self, device, widget):
        if self.selectDeviceFun is not None:
            print("Selecting device")
            if self.selectedDevice != device and device is not None:
                widget.setStyleSheet("background-color: red")
                widget.update()
            else:
                device = None
                widget = None
            if self.selectedDeviceWidget is not None:
                self.selectedDeviceWidget.setStyleSheet("")
                self.selectedDeviceWidget.update()
            self.selectDeviceFun(device)
            self.selectedDevice = device
            self.selectedDeviceWidget = widget

    def addWidgetToLayout(self, widget):
        self.box.addWidget(widget)
        self.widgetList.append(widget)

    def clearWidgets(self):
        for w in self.widgetList:
            self.box.removeWidget(w)
        self.widgetList.clear()

    def generateReservationHandleFun(self, device, t):
        def fun():
            t.reserveDevice(device)
        return fun

    def generateReleaseHandleFun(self, device, t):
        def fun():
            t.releaseDevice(device)
        return fun

    def generateSelectDeviceFun(self, device, widget):
        def fun():
            if self.selectDeviceFun is not None:
                self.selectDevice(device, widget)
        return fun

    def newDevices(self, devTypes):
        # We simply override the argument here
        devTypes = control.DeviceType._deviceTypes
        self.clearWidgets()
        for t in devTypes.keys():
            if len(devTypes[t].getVisableDevices()) > 0:
                detectedLabel = QLabel(self)
                detectedLabel.setText("Detected:")
                self.addWidgetToLayout(detectedLabel)
            for dev in devTypes[t].getVisableDevices():
                button = QPushButton(self)
                button.clicked.connect(self.generateReservationHandleFun(dev, devTypes[t]))
                button.setText(str(dev.uid))
                self.addWidgetToLayout(button)
            reservedLabel = QLabel(self)
            reservedLabel.setText("Reserved:")
            self.addWidgetToLayout(reservedLabel)
            for dev in devTypes[t].getReservedDevices():
                button = QPushButton(self)
                miniLayout = QHBoxLayout(self)
                miniWidget = QWidget(self)
                miniWidget.setLayout(miniLayout)

                button.clicked.connect(self.generateReleaseHandleFun(dev, devTypes[t]))
                button.setText(str(dev.uid))
                miniLayout.addWidget(button)

                if self.selectDeviceFun is not None:
                    deviceButton = QPushButton(self)
                    deviceButton.clicked.connect(self.generateSelectDeviceFun(dev, miniWidget))
                    deviceButton.setText("Select")
                    miniLayout.addWidget(deviceButton)

                self.addWidgetToLayout(miniWidget)
        self.widg.update()

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

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impyrium")
        self.setMinimumSize(800, 500)

        # None registry is the control box
        commands = aitpi.getCommandsByRegistry(None)
        categories = set()
        for c in commands:
            categories.add(c['id'])

        view2 = ItemScrollView([ControlsTypeSection(cat) for cat in categories])
        self.currentControlList = ItemScrollView([], self)
        mainWidget = QWidget()
        mainLayout = QHBoxLayout()
        tabwidget = QTabWidget()

        tabwidget.addTab(Aitpi(self), "Shortcuts")
        tabwidget.addTab(view2, "Global Controls")
        tabwidget.addTab(self.currentControlList, "Device Controls")
        devList = DeviceList(self, self.selectDevice)
        mainLayout.addWidget(devList)
        mainLayout.addWidget(tabwidget)

        self.selectedDevControls = []

        mainWidget.setLayout(mainLayout)
        device_thread.worker_
        control.registerNewDeviceFun(devList)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(mainWidget)

        self.isLinux = sys.platform.startswith('linux')

    def selectDevice(self, dev):
        for w in self.selectedDevControls:
            self.currentControlList.removeItem(w)
        self.selectedDevControls.clear()
        if dev is not None:
            categories = dev.deviceType.getControlCategories()
            for cat in categories:
                self.selectedDevControls.append(ControlsTypeSection(cat))
            for w in self.selectedDevControls:
                self.currentControlList.addItem(w)
        self.currentControlList.update()

    def keyPressEvent(self, event):
        if self.isLinux:
            aitpi.pyqt6KeyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.isLinux:
            aitpi.pyqt6KeyReleaseEvent(event)


