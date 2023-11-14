from .aitpi.src import aitpi
from .aitpi.src.aitpi import router

from . import device_thread
from enum import Enum

CONTROL_BUTTON   = 0
CONTROL_SLIDER   = 1
CONTROL_DIAL     = 2
CONTROL_FILE     = 3
CONTROL_STRING   = 4
CONTROL_DATE     = 5
CONTROL_ENUM     = 6

class ControlEvents(Enum):
    VALUE_SET = "VALUE_SET"

class ControlButton():
    def __init__(self) -> None:
        pass

class ControlSlider():
    def __init__(self, minimum, maximum, increment) -> None:
        self.min = minimum
        self.max = maximum
        self.increment = increment
        res = (self.max - self.min) / self.increment
        # Make sure our max always lines up 
        self.max = self.min + int(res) * self.increment

    def convertSliderValue(self, value):
        value = (self.increment * value) + self.min
        return value

    def generateSliderValues(self):
        distance = abs(self.max - self.min)
        counts = abs(distance / self.increment)
        #       min    max       increment
        print(counts)
        return (0,     int(counts),   1)

BUTTON_CONTROLS = {ControlButton, CONTROL_FILE, CONTROL_DATE, CONTROL_STRING}
ENCODER_CONTROLS = {CONTROL_DIAL, ControlSlider, CONTROL_ENUM}


controls_ = {}
newDeviceFun_ = None
signal_ = None

class Control():
    def __init__(self, category, name, controlType, sendFun, deviceAutoReserve=False):
        self.name = name
        self.controlType = controlType
        self.sendFun = sendFun
        self.category = category
        self.deviceAutoReserve = deviceAutoReserve
        self.hasReleased = False
        self.data = {}
        if type(self.controlType) in BUTTON_CONTROLS:
            self.inputType = "button"
        elif type(self.controlType) in ENCODER_CONTROLS:
            self.inputType = "encoder"
        else:
            raise Exception("Invalid control type")

    def consume(self, msg):
        if (msg.name == self.name):
            self.sendFun(msg, msg.event, DeviceType.getReservedDevices())

# Simple helper class that defines a devices unique id, and stores reservation state
class Device():
    def __init__(self, uid, deviceType):
        self.uid = uid
        if type(deviceType) == str:
            deviceType = DeviceType._deviceTypes[deviceType]
        if type(deviceType) != DeviceType:
            raise Exception("deviceType needs to be a DeviceType(), or the name string")
        self.deviceType = deviceType
        self.reserveTask = None
        self.reserveTime = 0.0

    def __str__(self):
        return f"<{self.uid}>"

    def __eq__(self, other):
        if type(other) != Device:
            return False
        return self.uid == other.uid

    def __hash__(self):
        return self.uid.__hash__()

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

def setDeviceFree(device):
    for t in DeviceType._deviceTypes:
        if device.uid in t.reservedDevices:
            t.releaseDevice(device)

# We allow the users to define devices types so that different types of devices can work
class DeviceType():
    _deviceTypes = {}

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
        self.visableDevices = set()

    def hasCategory(self, category):
        return category in self.controlCategories

    def getControlCategories(self):
        return list(self.controlCategories)

    def reserveAllDevices(self, autoReserve=False):
        if self.reserveDeviceFun is None:
            return
        for dev in list(self.visableDevices):
            self.reserveDevice(dev, autoReserve=autoReserve)

    def isDevReserved(self, device):
        return device in self.reservedDevices

    def getVisableDevices(self):
        return self.visableDevices

    def getReservedDevices(self):
        return self.reservedDevices

    def sendUpdateSignal(self):
        global newDeviceFun_
        if newDeviceFun_ is not None:
            # TODO: This is really jank
            newDeviceFun_.objectNameChanged.emit("")

    def detect(self):
        global signal_
        devices = self.detector()
        visNew = set()
        resNew = set()
        for device in devices:
            if type(device) != Device:
                raise Exception("All detected devices need to be Device()")
            if device not in self.visableDevices:
                if self.reserveDeviceFun is not None:
                    visNew.add(device)
                else:
                    resNew.add(device)
        hasNew = self.visableDevices.intersection(visNew).union(self.reservedDevices.intersection(resNew))
        self.visableDevices = self.visableDevices.union(visNew)
        self.reservedDevices = self.reservedDevices.union(resNew)
        if (hasNew != visNew.union(resNew)):
            self.sendUpdateSignal()
        self.scheduleDetection()

    def scheduleDetection(self):
        if self.detector is not None:
            device_thread.scheduleItem(self.pollRate, self.detect)

    def scheduleAutoTimeout(self, device):
        if self.autoReservationTimeout is not None and self.releaseDeviceFun is not None:
            device_thread.scheduleItem(self.autoReservationTimeout, lambda: self.releaseDevice(device))

    def releaseDevice(self, device):
        if (self.releaseDeviceFun is not None):
            if (self.reserveCheck is not None and not self.reserveCheck(device)):
                # We know the device has already been released
                return
            self.releaseDeviceFun(device)
            self.reservedDevices.remove(device)
            self.sendUpdateSignal()

    def reserveDevice(self, device, autoReserve=False):
        if (self.reserveDeviceFun is not None):
            self.reserveDeviceFun(device)
            self.reservedDevices.add(device)
            self.visableDevices.remove(device)
            self.sendUpdateSignal()
            if autoReserve:
                self.scheduleAutoTimeout(device)

    @staticmethod
    def getAllDeviceTypes(category):
        ret = []
        for key in DeviceType._deviceTypes.keys():
            t = DeviceType._deviceTypes[key]
            if t.hasCategory(category):
                ret.append(t)
        return ret

    @staticmethod
    def getControlDevList(ctrl):
        devices = set()
        for t in DeviceType.getAllDeviceTypes(ctrl.category):
            if ctrl.deviceAutoReserve:
                t.reserveAllDevices(autoReserve=True)
            devices.update(t.getReservedDevices())
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
