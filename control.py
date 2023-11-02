from aitpi.src import aitpi
import device_thread
import defaults

CONTROL_BUTTON   = 0
CONTROL_SLIDER   = 1
CONTROL_DIAL     = 2
CONTROL_FILE     = 3
CONTROL_STRING   = 4
CONTROL_DATE     = 5
CONTROL_ENUM     = 6

BUTTON_CONTROLS = {CONTROL_BUTTON, CONTROL_FILE, CONTROL_DATE, CONTROL_ENUM, CONTROL_STRING}
ENCODER_CONTROLS = {CONTROL_DIAL, CONTROL_SLIDER, CONTROL_ENUM}

controls_ = {}
newDeviceFun_ = None

def getControls():
    global controls_
    return controls_

def addToAitpi(control):
    aitpi.addCommandToRegistry(defaults.COMMAND_REGISTRY_FILE)

def registerControl(control):
    global controls_
    if (control.category not in controls_):
        controls_[control.category] = []
    controls_[control.category].append(control)

class Control():
    def __init__(self, id, name, category, controlType, sendFun):
        self.name = name
        self.controlType = controlType
        self.sendFun = sendFun
        self.category = category


    def consume(msg):
        # TODO: What here?
        pass


def sendSomething(command, args):
    print("Sent", command.name, "with", args)

# Simple helper class that defines a devices unique id, and stores reservation state
class Device():
    def __init__(self, uid):
        self.uid = uid
        self.reserveTask = None
        self.reserveTime = 0.0

    def __eq__(self, other):
        return self.uid == other.uid

    def __hash__(self):
        return self.uid.__hash__()


def registerNewDeviceFun(fun):
    global newDeviceFun_
    newDeviceFun_ = fun

def registerDeviceType(devType):
    DeviceType._deviceTypes[devType.name] = devType
    devType.scheduleDetection()



# We allow the users to define devices types so that different types of devices can work
class DeviceType():
    _deviceTypes = {}

    def __init__(self, name, detector=None, pollRate=1, reserveDevice=None, releaseDevice=None, autoReservationTimeout=None, reserveCheck=None):
        self.name = name
        self.detector = detector
        self.pollRate = pollRate
        self.reserveCheck = reserveCheck
        self.reserveDevice = reserveDevice
        self.releaseDevice = releaseDevice
        self.autoReservationTimeout = autoReservationTimeout
        self.ownsDevice = False
        self.reservedDevices = set()
        self.visableDevices = set()

    def getVisableDevices(self):
        return self.visableDevices

    def getReservedDevices(self):
        return self.reservedDevices

    def detect(self):
        devices = self.detector()
        visNew = set()
        resNew = set()
        for device in devices:
            if type(device) != Device:
                raise Exception("All detected devices need to be Device()")
            print(f"detected a {self.name} device {device.uid}")
            if device not in self.visableDevices:
                if self.reserveDevice is not None:
                    visNew.add(device)
                else:
                    resNew.add(device)
        self.visableDevices = self.visableDevices.union(visNew)
        self.reservedDevices = self.reservedDevices.union(resNew)
        if (self.reservedDevices != resNew or self.visableDevices != visNew):
            global newDeviceFun_
            if newDeviceFun_ is not None:
                newDeviceFun_(DeviceType._deviceTypes)

        self.scheduleDetection()

    def scheduleDetection(self):
        if self.detector is not None:
            device_thread.scheduleItem(self.pollRate, self.detect)

    def releaseDevice(self, device):
        if (self.releaseDevice is not None):
            self.releaseDevice(device)
            self.reservedDevices.remove(device)

    def reserveDevice(self, device):
        if (self.reserveDevice is not None):
            self.reserveDevice(device)
            self.reservedDevices.add(device)
            self.visableDevices.remove(device)
