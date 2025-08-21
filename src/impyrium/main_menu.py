import sys
import time

from .popups.status_sidebar import StatusSidebar

from .aitpi.src.aitpi import router
from .aitpi.src import aitpi

from .aitpi_signal import AitpiSignalExecutor

from . import helpers
from .aitpi_signal import AitpiSignal
from . import signals
from .thread_safe_queue import ThreadSafeQueue
from .aitpi_widget import Aitpi
from . import device_thread
from . import control
from .worker_thread import WorkerThread
import os

from .text_display import TextDisplay

from .widgets.item_scroll_view import ItemScrollView

from .popups import build_a_popup
from .popups import device_info_popup

from . import common_css
from .widgets.custom_button import ImpPushButton
import typing
import PySide6
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QComboBox,
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QHBoxLayout,
)

from .popups.single_select_popup import SingleSelectPopup

def getFileConsumer(msg):
    fun = msg['fun']
    directory = msg['directory']
    types = msg['types']
    file = helpers.getFileFromDialog(types, directory)
    fun(file)

def selectItemConsumer(msg):
    fun = msg['fun']
    items = msg['items']
    name = msg['name']
    devices = msg['devices']
    dialog = SingleSelectPopup(fun, name, items, devices)
    devs, res = dialog.popUp()
    fun((devs, res))

def buildPopupConsumer(msg):
    fun = msg['fun']
    name = msg['name']
    components = msg['components']
    devices = msg['devices']
    dialog = build_a_popup.BuildAPopup(fun, name, devices, components)
    devs, res = dialog.popUp()
    fun((devs, res))

def addStatusEntry(msg):
    action, text = msg
    if action == "REMOVE":
        StatusSidebar.removeEntry(text)
    elif action == "ADD":
        StatusSidebar.addEntry(text)

def getScriptPath():
    return os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")

def printAllOfType(item, t):
    for d in dir(item):
        if (type(item.__getattribute__(d)) == t):
            print(d)

class ControlsScrollView(QWidget):
    def __init__(self, category, autoReserve, abilities=set()):
        super(ControlsScrollView, self).__init__()
        layout = QVBoxLayout(self)
        self.autoReserve = autoReserve
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        controls = control.getControls()
        self.worker = WorkerThread()
        self.worker.start()
        self.count = 0
        if category in controls:
            for c in controls[category]:
                mod = self.getObjectMod(c)
                if mod is None:
                    print(f"Mod is None for {c.name}, cannot do anything with this, please fix")
                    continue
                for item in mod:
                    layout.addWidget(item)
                    if not c.enabled or (not c.getRequiredAbilities().issubset(abilities) and not autoReserve):
                        item.hide()
                    else:
                        self.count += 1
        else:
            print("Could not find any controls for ", category)

    def generateButtonCallbackFun(self, ctrl, event):
        def fun():
            if ctrl.enabled:
                ctrl.handleGuiEvent(event, control.DeviceType.getControlDevList(ctrl, self.autoReserve))
        return fun

    def generateSliderCallbackFun(self, ctrl):
        def fun(value):
            if ctrl.enabled:
                def item():
                    ctrl.setValueFromSlider(value)
                    ctrl.handleGuiEvent(control.ControlEvents.VALUE_SET, control.DeviceType.getControlDevList(ctrl, self.autoReserve))

                if 'event' in ctrl.data and ctrl.data['event'] is not None:
                    self.worker.removeItem(ctrl.data['event'])
                ctrl.data['event'] = self.worker.scheduleItem(0.5, item)
        return fun

    def getObjectMod(self, ctrl):
        if type(ctrl) == control.ControlButton or type(ctrl) == control.ControlFile or issubclass(type(ctrl), control.ControlButton):
            button = ImpPushButton()
            button.setMinimumHeight(25)
            button.setText(ctrl.name)
            button.pressed.connect(self.generateButtonCallbackFun(ctrl, control.ControlEvents.BUTTON_PRESS))
            button.released.connect(self.generateButtonCallbackFun(ctrl, control.ControlEvents.BUTTON_RELEASE))
            # button.setStyleSheet(f"QWidget{{ border-bottom: 1px solid grey; }} {common_css.HOVER_EFFECT}")
            return [button]
        if type(ctrl) == control.ControlSlider:
            ret = QSlider(Qt.Orientation.Horizontal)
            res = ctrl.generateSliderValues()
            ret.setMinimum(res[0])
            ret.setMaximum(res[1])
            ret.setMinimumHeight(25)
            label = QLabel(ctrl.name)
            ret.valueChanged.connect(self.generateSliderCallbackFun(ctrl))
            label.setBuddy(ret)
            # ret.setStyleSheet("QWidget{ border-right: 1px solid grey; border-left: 1px solid grey }")
            return [label, ret]
        return None

class ControlsTypeSection(QWidget):
    def __init__(self, category, autoReserve, abilities=set(), parent: QWidget = None):
        super().__init__(parent)
        container = QWidget()
        containerLayout = QVBoxLayout()
        subwidget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        button = ImpPushButton(container)
        button.setText(category)
        button.clicked.connect(self.buttonPressed)
        subwidget.setStyleSheet('QWidget{ border: 1px solid grey; }')
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)
        self.controlsView = ControlsScrollView(category, autoReserve, abilities)
        self.controlsView.setStyleSheet(f"QWidget{{ border: revert; }}")
        if self.controlsView.count > 0:
            self.showing = True
            self.controlsView.show()
        else:
            self.showing = False
            self.controlsView.hide()
        layout.addWidget(self.controlsView)
        subwidget.setLayout(layout)
        containerLayout.addWidget(subwidget)
        self.setLayout(containerLayout)

    def buttonPressed(self):
        self.showing = not self.showing
        if (self.showing):
            self.controlsView.show()
        else:
            self.controlsView.hide()

class DeviceList(QScrollArea):
    def __init__(self, parent: QWidget = None, selectDeviceFun = None) -> None:
        super(DeviceList, self).__init__(parent)
        self.widg = QWidget()
        self.box = QVBoxLayout(self.widg)
        self.box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self.widg)
        self.setWidgetResizable(True)
        self.widgetList = []
        self.selectedDevice = None
        self.selectedDeviceWidget = None
        self.selectDeviceFun = selectDeviceFun
        router.addConsumer(signals.DEVICE_LIST_UPDATE, self)

    def selectDevice(self, device, widget):
        if self.selectDeviceFun is not None:
            print("Selecting device")
            if self.selectedDevice != device and device is not None:
                widget.setStyleSheet(f"background-color: {common_css.ACCENT_COLOR}")
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
            w.setStyleSheet("")
            for child in w.children():
                w.setStyleSheet("")
                child.deleteLater()
            self.box.removeWidget(w)
        self.widgetList.clear()

    def removeWidget(self, w):
        self.box.removeWidget(w)
        print(self.widgetList, w)
        self.widgetList.remove(w)

    def generateReservationHandleFun(self, device, t):
        def fun():
            t.reserveDevice(device)
        return fun

    def generateReleaseHandleFun(self, device, t, w):
        def fun():
            if device == self.selectedDevice:
                self.selectDevice(None, None)
            t.releaseDevice(device)
        return fun

    def generateSelectDeviceFun(self, device, widget):
        def fun():
            if self.selectDeviceFun is not None:
                self.selectDevice(device, widget)
        return fun

    def generateInfoDeviceFun(self, device : control.Device):
        def fun():
            info = device.getInfo()
            popup = device_info_popup.DeviceInfoPopup("Device Info", info, device.getLogo())
            popup.popUp()
        return fun

    def consume(self, msg):
        self.newDevices(msg)

    def newDevices(self, devTypes):
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
        self.clearWidgets()
        for t in devTypes.keys():
            unreserved = devTypes[t].getUnreservedDevices()
            if len(unreserved) > 0:
                detectedLabel = QLabel(self)
                detectedLabel.setText(f"{t} detected:")
                self.addWidgetToLayout(detectedLabel)
            for dev in unreserved:
                miniWidget = QWidget(self)
                miniLayout = QHBoxLayout(miniWidget)
                miniWidget.setLayout(miniLayout)

                button = ImpPushButton(self)
                button.clicked.connect(self.generateReservationHandleFun(dev, devTypes[t]))
                button.setText(dev.getFullName())
                button.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)

                miniLayout.addWidget(generateInfoButton(), 1)
                miniLayout.addWidget(button, 10)

                self.addWidgetToLayout(miniWidget)

            reservedLabel = QLabel(self)
            reserved = devTypes[t].getReservedDevices()
            if len(reserved) > 0:
                reservedLabel.setText(f"{t} reserved:")
                self.addWidgetToLayout(reservedLabel)
            for dev in reserved:
                miniWidget = QWidget(self)
                button = ImpPushButton(miniWidget)
                miniLayout = QHBoxLayout(miniWidget)
                miniWidget.setLayout(miniLayout)
                button.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)

                button.clicked.connect(self.generateReleaseHandleFun(dev, devTypes[t], miniWidget))
                button.setText(dev.getName())
                miniLayout.addWidget(generateInfoButton())
                miniLayout.addWidget(button)

                if self.selectDeviceFun is not None:
                    deviceButton = ImpPushButton(miniWidget)
                    deviceButton.clicked.connect(self.generateSelectDeviceFun(dev, miniWidget))
                    deviceButton.setText("select")
                    deviceButton.setSizePolicy(PySide6.QtWidgets.QSizePolicy.Policy.Expanding, PySide6.QtWidgets.QSizePolicy.Policy.Minimum)
                    miniLayout.addWidget(deviceButton)
                self.addWidgetToLayout(miniWidget)
        self.update()

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
    def __init__(self, logo, title):
        super().__init__()
        if title is None:
            self.setWindowTitle("Impyrium")
        else:
            self.setWindowTitle(title)
        self.setStyleSheet(common_css.MAIN_STYLE)
        self.setMinimumSize(800, 500)
        self.fileCallback = None
        self.selectedDevice = None
        self.signalExec = AitpiSignalExecutor()
        self.signalExec.start()

        # None registry is the control box
        commands = aitpi.getCommandsByRegistry(None)
        categories = set()
        for c in commands:
            categories.add(c['id'])

        view2 = ItemScrollView([ControlsTypeSection(cat, True) for cat in categories])
        view2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.currentControlList = ItemScrollView([], self)
        self.currentControlList.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)


        def updateCurrentControlList(devlist):
            if self.selectedDevice is not None and self.selectedDevice not in devlist:
                self.selectDevice(None)
        router.addConsumer(signals.DEVICE_LIST_UPDATE, updateCurrentControlList)

        mainWidget = QWidget(self)
        mainLayout = QHBoxLayout()
        tabwidget = QTabWidget(self)
        textDisplay = TextDisplay(self)

        if logo is not None:
            self.setWindowIcon(QtGui.QIcon(logo()))
        else:
            self.setWindowIcon(QtGui.QIcon(helpers.getImageForPyQt("logo")))

        tabwidget.addTab(self.currentControlList, "Device")
        tabwidget.addTab(view2, "Global")
        tabwidget.addTab(Aitpi(self), "Keys")
        tabStyle = f""" 
        QTabBar::tab:selected {{background-color: {common_css.ACCENT_COLOR}; }}
        QTabBar::tab {{background-color: {common_css.MAIN_COLOR}; }}
        QTabWidget>QWidget>QWidget{{ background: gray; }}
        QTabWidget::pane {{ border-top: 2px solid {common_css.ACCENT_COLOR}; }}
        """
        # tabwidget.setStyleSheet(f"QWidget{{ background-color: {common_css.MAIN_COLOR} }}")
        tabwidget.setStyleSheet(tabStyle)
        devList = DeviceList(self, self.selectDevice)
        devList.setMinimumSize(250, 10)
        mainLayout.addWidget(devList)
        mainLayout.addWidget(tabwidget)
        mainLayout.addWidget(textDisplay)

        self.selectedDevControls = []

        mainWidget.setLayout(mainLayout)
        router.addConsumer([signals.GET_FILE], getFileConsumer)
        router.addConsumer([signals.SELECT_ITEM], selectItemConsumer)
        router.addConsumer([signals.ADD_SIDEBAR_STATUS_ENTRY], addStatusEntry)
        router.addConsumer([signals.CUSTOM_POPUP], buildPopupConsumer)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(mainWidget)
        self.isLinux = sys.platform.startswith('linux')

    def selectDevice(self, dev):
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

    def keyPressEvent(self, event):
        if self.isLinux:
            aitpi.PySide6KeyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.isLinux:
            aitpi.PySide6KeyReleaseEvent(event)

    def closeEvent(self, event):
        self.end()
        event.accept()

    def close(self):
        self.end()
        super().close()

    def end(self):
        StatusSidebar.stop()
