from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QDockWidget,
)
from .item_scroll_view import ItemScrollView
from .custom_button import ImpPushButton
from .. import signals
from .. import router
from PySide6.QtCore import Qt
from .. import common_css
from typing import List
from .. import control
from ..popups import device_info_popup
from PySide6 import QtGui
import PySide6
from .control_menu import ControlsTypeSection
from ..text_display import TextDisplay
from .. import helpers
from ..keybinding_widget import KeybindingWidget
from typing import Dict, Callable, List
from .. import work_queue

class DeviceList(QScrollArea):
    _deviceSelectFuns = []
    _allDeviceLists = []
    _allSelectDeviceFuns: Dict[control.Device, List[Callable]] = {}
    def __init__(self, parent: QWidget = None, selectDeviceFun = None, filter = lambda x: False, addToGlobal = True) -> None:
        super(DeviceList, self).__init__(parent)
        self.widg = QWidget()
        self.box = QVBoxLayout(self.widg)
        self.box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.widg)
        self.setWidgetResizable(True)
        self.widgetList: List[QWidget] = []
        self.selectedDevice = None
        self.selectedDeviceWidget: QWidget = None
        if selectDeviceFun is not None:
            self._deviceSelectFuns.append(selectDeviceFun)
        router.addConsumer(signals.DEVICE_LIST_UPDATE, self)
        self.filter = filter
        if addToGlobal:
            self._allDeviceLists.append(self)

    def selectDevice(self, device, widget: QWidget):
        if len(self._deviceSelectFuns) > 0:
            if self.selectedDevice != device and device is not None:
                widget.setStyleSheet(f"background-color: {common_css.ACCENT_COLOR}")
                widget.update()
            else:
                device = None
                widget = None
            if self.selectedDeviceWidget is not None:
                self.selectedDeviceWidget.setStyleSheet("")
                self.selectedDeviceWidget.update()
            for fun in self._deviceSelectFuns:
                fun(device)
            self.selectedDevice = device
            self.selectedDeviceWidget = widget

    def addWidgetToLayout(self, widget):
        self.box.addWidget(widget)
        # self.widgetList.append(widget)

    def removeWidget(self, w):
        self.box.removeWidget(w)
        self.widgetList.remove(w)

    def generateReservationHandleFun(self, device: control.Device, t: control.DeviceType):
        def fun():
            t.reserveDevice(device)
        return fun

    def generateReleaseHandleFun(self, device: control.Device, t: control.DeviceType, w: QWidget):
        def fun():
            if device == self.selectedDevice:
                self.selectDevice(None, None)
            t.releaseDevice(device)
        return fun

    @staticmethod
    def generateSelectDeviceFun(device: control.Device):
        def fun():
            for call in DeviceList._allSelectDeviceFuns[device]:
                call()
        return fun


    def addSelectDeviceFun(self, device: control.Device, widget: QWidget):
        def fun():
            self.selectDevice(device, widget)
        if device not in DeviceList._allSelectDeviceFuns:
            DeviceList._allSelectDeviceFuns[device] = []
        DeviceList._allSelectDeviceFuns[device].append(fun)

    def generateInfoDeviceFun(self, device: control.Device):
        def fun():
            info = device.getInfo()
            popup = device_info_popup.DeviceInfoPopup("Device Info", info, device.getLogo())
            popup.popUp()
        return fun

    @staticmethod
    def consume(msg):
        DeviceList._allSelectDeviceFuns.clear()
        for devlist in DeviceList._allDeviceLists:
            DeviceList.newDevices(devlist, msg)

    @staticmethod
    def newDevices(self: "DeviceList", devTypes):
        def generateInfoButton():
            infoButton = ImpPushButton(miniWidget)
            infoButton.setGeometry(50, 50, 50, 50)
            infoButton.clicked.connect(self.generateInfoDeviceFun(dev))
            if dev.getLogo() is not None:
                infoButton.setIcon(QtGui.QIcon(dev.getLogo()))
                infoButton.setIconSize(PySide6.QtCore.QSize(35,35))
            else:
                infoButton.setText("I")
                infoButton.setIconSize(PySide6.QtCore.QSize(35,35))
            infoButton.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Minimum, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)
            return infoButton
        # We simply override the argument here
        devTypes = control.DeviceType._deviceTypes
        # Clear all widgets from the box layout
        while self.box.count():
            child = self.box.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for t in devTypes.keys():
            unreservedTemp = devTypes[t].getUnreservedDevices()
            unreserved = []
            for dev in unreservedTemp:
                if self.filter(dev):
                    continue
                unreserved.append(dev)

            if len(unreserved) > 0:
                detectedLabel = QLabel(self)
                detectedLabel.setText(f"{t} detected:")
                self.addWidgetToLayout(detectedLabel)
            for dev in unreserved:
                if self.filter(dev):
                    continue
                miniWidget = QWidget(self)
                miniLayout = QHBoxLayout(miniWidget)
                miniWidget.setLayout(miniLayout)

                button = ImpPushButton(self)
                button.clicked.connect(self.generateReservationHandleFun(dev, devTypes[t]))
                button.setText(f"Reserve\n{dev.getFullName()}")
                button.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)

                miniLayout.addWidget(generateInfoButton(), 1)
                miniLayout.addWidget(button, 10)

                self.addWidgetToLayout(miniWidget)

            reservedTemp = devTypes[t].getReservedDevices()
            reserved = []
            for dev in reservedTemp:
                if self.filter(dev):
                    continue
                reserved.append(dev)

            if len(reserved) > 0:
                reservedLabel = QLabel(self)
                reservedLabel.setText(f"{t} reserved:")
                self.addWidgetToLayout(reservedLabel)
            for dev in reserved:
                miniWidget = QWidget(self)
                button = ImpPushButton(miniWidget)
                miniLayout = QHBoxLayout(miniWidget)
                miniWidget.setLayout(miniLayout)
                button.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)

                button.clicked.connect(self.generateReleaseHandleFun(dev, devTypes[t], miniWidget))
                button.setText(f"Release\n{dev.getName()}")
                miniLayout.addWidget(generateInfoButton())
                miniLayout.addWidget(button)

                if len(self._deviceSelectFuns) > 0:
                    deviceButton = ImpPushButton(miniWidget)
                    self.addSelectDeviceFun(dev, miniWidget)
                    deviceButton.clicked.connect(DeviceList.generateSelectDeviceFun(dev))
                    deviceButton.setText("Select")
                    deviceButton.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)
                    miniLayout.addWidget(deviceButton)
                self.addWidgetToLayout(miniWidget)
        self.update()


class DeviceListDock(QDockWidget):
    def __init__(self, parent=None, selectDeviceCallback=None):
        super().__init__("Device List", parent)
        self.selectDeviceCallback = selectDeviceCallback
        self.deviceList = DeviceList(self, selectDeviceCallback)
        self.setWidget(self.deviceList)


class MainImpyrium(QWidget):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.exec = work_queue.WorkQueueExecutor()
        self.exec.start()

        view2 = ItemScrollView([ControlsTypeSection(cat, True) for cat in categories])
        view2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.currentControlList = ItemScrollView([], self)
        self.currentControlList.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.selectedDevice = None

        mainLayout = QHBoxLayout()
        tabwidget = QTabWidget(self)
        textDisplay = TextDisplay(self)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tabwidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        textDisplay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tabwidget.addTab(self.currentControlList, "Single Device")
        tabwidget.addTab(view2, "Global")
        tabwidget.setCurrentIndex(1)
        tabwidget.addTab(KeybindingWidget(self), "Keyboard Shortcuts")

        tabwidget.setStyleSheet(common_css.TAB_STYLE)

        mainLayout.addWidget(tabwidget)
        mainLayout.addWidget(textDisplay)
        self.setLayout(mainLayout)
        self.selectedDevControls = []
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def selectDevice(self, dev: control.Device):
        self.selectedDevice = dev
        for w in self.selectedDevControls:
            self.currentControlList.removeItem(w)
        self.selectedDevControls.clear()
        if dev is not None:
            categories = dev.deviceType.getControlCategories()
            for cat in categories:
                self.selectedDevControls.append(ControlsTypeSection(cat, False, dev.getAbilities()))
            for w in self.selectedDevControls:
                self.currentControlList.addItem(w)
        self.currentControlList.update()

        def updateCurrentControlList(devlist):
            if self.selectedDevice is not None and self.selectedDevice not in devlist:
                self.selectDevice(None)
        router.addConsumer(signals.DEVICE_LIST_UPDATE, updateCurrentControlList)
