from .aitpi.src import aitpi
from .aitpi.src.aitpi import router

from .thread_safe_queue import ThreadSafeQueue

from .aitpi_signal import AitpiSignal
from . import signals

from .text_display import TextDisplay

from . import device_thread
from enum import Enum

from . import helpers

import typing

class ControlEvents(Enum):
    VALUE_SET       = "VALUE_SET"
    BUTTON_PRESS    = "BUTTON_PRESS"
    BUTTON_RELEASE  = "BUTTON_RELEASE"

class RangeValue():
    def __init__(self, minimum, maximum, increment, default=None):
        if default is None:
            default = minimum
        self.min = minimum
        self.max = maximum
        self.inc = increment
        res = (self.max - self.min) / self.inc

        self.max = self.generateValidValue(self.max)
        self.value = self.generateValidValue(default)


    def generateValidValue(self, value):
        if value < self.min:
            value = self.min
        if value > self.max:
            value = self.max

        res = (value - self.min) / self.inc
        if (float(int(res)) != res):
            value = self.min + int(res) * self.inc 
        return value

    def sub(self):
        self.value = self.generateValidValue(self.value - self.inc)

    def add(self):
        self.value = self.generateValidValue(self.value + self.inc)

    def left(self):
        return self.sub()

    def right(self):
        return self.add()

    def setValue(self, value):
        self.value = self.generateValidValue(value)

    def getValue(self):
        return self.value

controls_ = {}
newDeviceFun_ = None
signal_ = None

class Control():
    def __init__(self, category, name, sendFun, deviceAutoReserve=False, enabled=True, requiredAbilities=set()):
        self.name = name
        self.sendFun = sendFun
        self.category = category
        self.deviceAutoReserve = deviceAutoReserve
        self.hasReleased = False
        self.data = {}
        self.inputType = "button"
        self.enabled = enabled
        self.requiredAbilities = requiredAbilities
        if type(self.requiredAbilities) != set:
            self.requiredAbilities = set(self.requiredAbilities)

    def getRequiredAbilities(self):
        return self.requiredAbilities

    def getValue(self):
        pass

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def consume(self, msg):
        if self.enabled:
            self.handleAitpi(msg)

    def handleGuiEvent(self, event, devList):
        if self.enabled:
            self.sendFun(self, event, devList)

    def handleAitpi(self, msg):
        if (msg.name == self.name):
            e = ControlEvents.BUTTON_PRESS
            if msg.event == aitpi.BUTTON_RELEASE:
                e = ControlEvents.BUTTON_RELEASE
            self.sendFun(self, e, DeviceType.getControlDevList(self))

class ControlButton(Control):
    pass #Base Control() is a button

class ControlDial(Control):
    pass #TODO:

class ControlFile(Control):
    fileQueue : ThreadSafeQueue = None
    allFiles = "All Files (*)"

    def __init__(self, category, name, sendFun, deviceAutoReserve=False, enabled=True, directory="", requiredAbilities=set()):
        super().__init__(category, name, sendFun, deviceAutoReserve, enabled, requiredAbilities)
        self.file = ""
        self.dir = directory

    def getValue(self):
        return self.file

    def runCallback(self, file):
        self.file = file
        if self.file is not None and self.file != "":
            self.sendFun(self, ControlEvents.VALUE_SET, DeviceType.getControlDevList(self))

    def requestFile(self):
        TextDisplay.print("Requesting file")
        AitpiSignal.send(signals.GET_FILE, {
            "fun": self.runCallback,
            "types": self.allFiles,
            "directory": self.dir,
        })

    def handleGuiEvent(self, event, devList):
        if event == ControlEvents.BUTTON_PRESS:
            return
        self.requestFile()

    def handleAitpi(self, msg):
        if msg.event == aitpi.BUTTON_PRESS:
            return
        if (msg.name == self.name):
            self.requestFile()

class ControlString(Control):
    pass #TODO:

class ControlDate(Control):
    pass #TODO:

class ControlSelector(ControlButton):
    def __init__(self, category, name, sendFun, items, deviceAutoReserve=False, enabled=True, requiredAbilities=set()):
        super().__init__(category, name, sendFun, deviceAutoReserve, enabled, requiredAbilities)
        self.items = items
        self.name = name
        self.sendFun = sendFun
        self.value = None

    def runCallback(self, result):
        devs, self.value = result
        if self.value is None:
            return
        if len(devs) == 0:
            devs = DeviceType.getControlDevList(self)
        else:
            for dev in devs:
                dev.reserve(True)
        self.sendFun(self, ControlEvents.VALUE_SET, devs)

    def requestSelection(self, devices=None):
        TextDisplay.print("Popping up selection")
        if devices is None or len(devices) == 0:
            devices = DeviceType.getAllPossibleControlDevList(self)
        AitpiSignal.send(signals.SELECT_ITEM, {
            "items": self.items,
            "name": self.name,
            "fun": self.runCallback,
            "devices": devices,
        })

    def handleGuiEvent(self, event, devList):
        if event == ControlEvents.BUTTON_PRESS:
            return
        self.requestSelection(devList)

    def handleAitpi(self, msg):
        if msg.event == aitpi.BUTTON_PRESS:
            return
        if (msg.name == self.name):
            self.requestSelection()

class ControlBuildAPopup(ControlButton):
    def __init__(self, category, name, sendFun, componentsFun, deviceAutoReserve=False, enabled=True):
        super().__init__(category, name, sendFun, deviceAutoReserve, enabled)
        self.componentsFun = componentsFun
        self.name = name
        self.sendFun = sendFun
        self.value = None

    def runCallback(self, result):
        devs, self.value = result
        if self.value is None:
            return
        if len(devs) == 0:
            devs = DeviceType.getControlDevList(self)
        else:
            for dev in devs:
                dev.reserve(True)
        self.sendFun(self, ControlEvents.VALUE_SET, devs)

    def requestPopup(self, devices=None):
        if devices is None or len(devices) == 0:
            devices = DeviceType.getAllPossibleControlDevList(self)
        AitpiSignal.send(signals.CUSTOM_POPUP, {
            "components": self.componentsFun(),
            "name": self.name,
            "fun": self.runCallback,
            "devices": devices,
        })

    def handleGuiEvent(self, event, devList):
        if event == ControlEvents.BUTTON_PRESS:
            return
        self.requestPopup(devList)

    def handleAitpi(self, msg):
        if msg.event == aitpi.BUTTON_PRESS:
            return
        if (msg.name == self.name):
            self.requestPopup()

class ControlSlider(Control):
    def __init__(self, category, name, sendFun, sliderRange : RangeValue, deviceAutoReserve=False, enabled=True, requiredAbilities=set()) -> None:
        super().__init__(category, name, sendFun, deviceAutoReserve, enabled, requiredAbilities)
        self.range = sliderRange
        self.inputType = "encoder"

    def convertSliderValue(self, value):
        value = (self.range.inc * value) + self.range.min
        return value

    def generateSliderValues(self):
        distance = abs(self.range.max - self.range.min)
        counts = abs(distance / self.range.inc)
        #       min    max       increment
        return (0,     int(counts),   1)

    def setValueFromSlider(self, value):
        self.range.setValue(self.convertSliderValue(value))

    def setValue(self, value):
        self.range.setValue(value)

    def getValue(self):
        return self.range.getValue()

    def handleAitpi(self, msg):
        if (msg.name == self.name):
            e = ControlEvents.VALUE_SET
            if msg.event == aitpi.ENCODER_LEFT:
                self.range.left()
            elif msg.event == aitpi.ENCODER_RIGHT:
                self.range.right()
            else:
                raise Exception(f"Invalid aitpi command {msg.event}")

            self.sendFun(self, e, DeviceType.getControlDevList(self))

# Simple helper class that defines a devices unique id, and stores reservation state
class Device():
    def __init__(self, uid, deviceType, name=None, abilities=set(), info={}):
        self.uid = uid
        self.name = name
        self.abilities = abilities
        self.info = info
        if self.name is None:
            self.name = str(self.uid)
        if type(deviceType) == str:
            deviceType = DeviceType._deviceTypes[deviceType]
        if not issubclass(type(deviceType), DeviceType):
            raise Exception("deviceType needs to be a DeviceType(), or the name string")
        self.deviceType = deviceType
        self.reserveTask = None
        self.reserveTime = 0.0

    def getLogo(self):
        return helpers.getImageForPyQt("default_device_logo")

    def getAbilities(self):
        return self.abilities

    def abilitiesSupported(self, abilities):
        if type(abilities) == set:
            return abilities.issubset(self.abilities)
        if type(abilities) == list:
            for ab in abilities:
                if ab not in self.abilities:
                    return False
            return True

    def getName(self):
        return self.name

    def getFullName(self):
        return f"{self.getName()} {self.uid}"

    def getInfo(self):
        return self.info

    def __str__(self):
        return self.getFullName()

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.uid == other.uid

    def __hash__(self):
        return self.uid.__hash__()

    def reserve(self, autoReserve=False):
        self.deviceType.reserveDevice(self, autoReserve)

    def isReserved(self):
        return self.deviceType.isDevReserved(self)

def registerNewDeviceFun(fun):
    global newDeviceFun_
    newDeviceFun_ = fun
    global signal_
    pass

def registerDeviceType(devType):
    DeviceType._deviceTypes[devType.name] = devType
    devType.scheduleDetection()

def removeReserved(device):
    for key in DeviceType._deviceTypes:
        t = DeviceType._deviceTypes[key]
        if device.uid in t.reservedDevices:
            t.removeReserved(device)

# We allow the users to define devices types so that different types of devices can work
class DeviceType():
    _deviceTypes : typing.Dict[str, 'DeviceType'] = {}

    def __init__(self, name, controlCategories = [], detector=None, pollRate=1, reserveDeviceFun=None, releaseDeviceFun=None, autoReservationTimeout=None, reserveCheck=None):
        self.name = name
        self.detector = detector
        self.pollRate = pollRate
        self.controlCategories = set(controlCategories)
        self.reserveCheck = reserveCheck
        self.reserveDeviceFun = reserveDeviceFun
        self.releaseDeviceFun = releaseDeviceFun
        self.autoReservationTimeout = autoReservationTimeout
        self.ownsDevice = False
        self.reservedDevices = set()
        self.devices = set()

    def hasCategory(self, category):
        return category in self.controlCategories

    def canReserve(self):
        return self.reserveDeviceFun is not None

    def getControlCategories(self):
        return list(self.controlCategories)

    def reserveAllDevices(self, autoReserve=False, abilities=set()):
        if not self.canReserve():
            return
        for dev in list(self.devices):
            if dev.abilitiesSupported(abilities):
                self.reserveDevice(dev, autoReserve=autoReserve)

    def isDevReserved(self, device):
        return device in self.reservedDevices

    def getUnreservedDevices(self, abilities=set()) -> typing.Set[Device]:
        if self.canReserve():
            ret = set()
            devs = self.devices.difference(self.reservedDevices)
            for dev in devs:
                if dev.abilitiesSupported(abilities):
                    ret.add(dev)
            return ret
        return set()

    def getReservedDevices(self, abilities=set()) -> typing.Set[Device]:
        ret = set()
        use = None
        if self.canReserve():
            use = self.reservedDevices
        else:
            use = self.devices
        for dev in use:
            if dev.abilitiesSupported(abilities):
                ret.add(dev)
        return ret

    def sendUpdateSignal(self):
        AitpiSignal.send(signals.DEVICE_LIST_UPDATE, self.devices)

    def detect(self):
        global signal_
        devices = self.detector()
        newDevices = set()
        for device in devices:
            if not issubclass(type(device), Device):
                raise Exception(f"All detected devices need to be Device() got '{type(device)}'")
            newDevices.add(device)
        if (self.devices != newDevices):
            self.devices = newDevices
            self.checkReservations()
            self.sendUpdateSignal()
        self.scheduleDetection()

    def scheduleDetection(self):
        if self.detector is not None:
            device_thread.scheduleItem(self.pollRate, self.detect)

    def scheduleAutoTimeout(self, device):
        if device.reserveTask is not None:
            device_thread.cancel(device.reserveTask)
            device.reserveTask = None
        if self.autoReservationTimeout is not None and self.releaseDeviceFun is not None:
            device.reserveTask = device_thread.scheduleItem(self.autoReservationTimeout, lambda: self.releaseDevice(device))

    def checkReservations(self):
        self.reservedDevices.difference_update(self.reservedDevices - self.devices)

    def releaseDevice(self, device):
        if (self.releaseDeviceFun is not None):
            device.reserveTask = None
            if (self.reserveCheck is not None and not self.reserveCheck(device)):
                # We know the device has already been released
                return
            self.releaseDeviceFun(device)
            if self.canReserve() and device in self.reservedDevices:
                self.reservedDevices.remove(device)
                self.sendUpdateSignal()

    def reserveDevice(self, device, autoReserve=False):
        if (self.reserveDeviceFun is not None):
            self.reserveDeviceFun(device)
            self.reservedDevices.add(device)
            self.sendUpdateSignal()
            if autoReserve:
                self.scheduleAutoTimeout(device)

    def getAllDevices(self, abilities=set()):
        devs = self.devices.union(self.reservedDevices)
        ret = set()
        for d in devs:
            if d.abilitiesSupported(abilities):
                ret.add(d)
        return ret

    @staticmethod
    def getAllDeviceTypes(category):
        ret = []
        for key in DeviceType._deviceTypes.keys():
            t = DeviceType._deviceTypes[key]
            if t.hasCategory(category):
                ret.append(t)
        return ret

    @staticmethod
    def getControlDevList(ctrl, shouldAutoReserve=True):
        devices = set()
        for t in DeviceType.getAllDeviceTypes(ctrl.category):
            if ctrl.deviceAutoReserve and shouldAutoReserve:
                t.reserveAllDevices(autoReserve=True, abilities=ctrl.requiredAbilities)
            devices.update(t.getReservedDevices(ctrl.requiredAbilities))
        return devices

    @staticmethod
    def getAllPossibleControlDevList(ctrl):
        devices = set()
        for t in DeviceType.getAllDeviceTypes(ctrl.category):
            devices.update(t.getAllDevices(ctrl.requiredAbilities))
        return devices

def getControls():
    global controls_
    return controls_

def init():
    # We use a None registry to add controls
    aitpi.addRegistry(None)

def addToAitpi(control):
    aitpi.addCommandToRegistry(None, control.name, control.category, control.inputType)
    router.addConsumer([control.category], control)

def registerControl(control):
    global controls_
    if (control.category not in controls_):
        controls_[control.category] = []
    controls_[control.category].append(control)
    addToAitpi(control)

def getControlsForDevice(device : Device):
    global controls_
    ret = {}
    for cat in device.deviceType.getControlCategories():
        ret[cat] = list(controls_[cat])

    return ret
