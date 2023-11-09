import aitpi
from aitpi import router

from . import device_thread

CONTROL_BUTTON   = 0
CONTROL_SLIDER   = 1
CONTROL_DIAL     = 2
CONTROL_FILE     = 3
CONTROL_STRING   = 4
CONTROL_DATE     = 5
CONTROL_ENUM     = 6

BUTTON_CONTROLS = {CONTROL_BUTTON, CONTROL_FILE, CONTROL_DATE, CONTROL_STRING}
ENCODER_CONTROLS = {CONTROL_DIAL, CONTROL_SLIDER, CONTROL_ENUM}

controls_ = {}
newDeviceFun_ = None
signal_ = None

def getControls():
    global controls_
    return controls_

def init():
    # We use a None registry to add controls
    aitpi.addRegistry(None)

def addToAitpi(control):
    aitpi.addCommandToRegistry(None, control.name, control.category, control.inputType)
    router.addConsumer([control.category], control)

def getDevList(ctrl):
    return []

def registerControl(control):
    global controls_
    if (control.category not in controls_):
        controls_[control.category] = []
    controls_[control.category].append(control)
    addToAitpi(control)

class Control():
    def __init__(self, category, name, controlType, sendFun):
        self.name = name
        self.controlType = controlType
        self.sendFun = sendFun
        self.category = category
        self.hasReleased = False
        if self.controlType in BUTTON_CONTROLS:
            self.inputType = "button"
        elif self.controlType in ENCODER_CONTROLS:
            self.inputType = "encoder"

    def consume(self, msg):
        if (msg.name == self.name):
            self.sendFun(self, msg.event, [])

# Simple helper class that defines a devices unique id, and stores reservation state
class Device():
    def __init__(self, uid):
        self.uid = uid
        self.reserveTask = None
        self.reserveTime = 0.0

    def __str__(self):
        return f"<{self.uid}>"

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return self.uid.__hash__()


def registerNewDeviceFun(fun):
    global newDeviceFun_
    newDeviceFun_ = fun
    global signal_
    pass

def registerDeviceType(devType):
    DeviceType._deviceTypes[devType.name] = devType
    devType.scheduleDetection()



# We allow the users to define devices types so that different types of devices can work
class DeviceType():
    _deviceTypes = {}

    def __init__(self, name, detector=None, pollRate=1, reserveDeviceFun=None, releaseDeviceFun=None, autoReservationTimeout=None, reserveCheck=None):
        self.name = name
        self.detector = detector
        self.pollRate = pollRate
        self.reserveCheck = reserveCheck
        self.reserveDeviceFun = reserveDeviceFun
        self.releaseDeviceFun = releaseDeviceFun
        self.autoReservationTimeout = autoReservationTimeout
        self.ownsDevice = False
        self.reservedDevices = set()
        self.visableDevices = set()

    def getVisableDevices(self):
        return self.visableDevices

    def getReservedDevices(self):
        return self.reservedDevices

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
            global newDeviceFun_
            if newDeviceFun_ is not None:
                newDeviceFun_.objectNameChanged.emit("")
                pass
                # signal_.emit("DeviceType._deviceTypes")
                # newDeviceFun_("Something")

        self.scheduleDetection()

    def scheduleDetection(self):
        if self.detector is not None:
            device_thread.scheduleItem(self.pollRate, self.detect)

    def releaseDevice(self, device):
        if (self.releaseDevice is not None):
            self.releaseDevice(device)
            self.reservedDevices.remove(device)

    def reserveDevice(self, device):
        if (self.reserveDeviceFun is not None):
            self.reserveDeviceFun(device)
            self.reservedDevices.add(device)
            self.visableDevices.remove(device)
