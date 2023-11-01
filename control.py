from aitpi.src import aitpi
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

_controls = {}

def getControls():
    global _controls
    return _controls

def addToAitpi(control):
    aitpi.addCommandToRegistry(defaults.COMMAND_REGISTRY_FILE)

def registerControl(control):
    global _controls
    if (control.category not in _controls):
        _controls[control.category] = []
    _controls[control.category].append(control)

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
        self.reserved = False
        self.reserveTime = 0.0


# We allow the users to define devices types so that different types of devices can work
class DeviceType():
    _deviceTypes = []
    _reservedDevices = {}
    _visableDevices = {}

    def __init__(self, name, detector=None, pollRate=1, reserveDevice=None, releaseDevice=None, reservationTimeout=None, reserveCheck=None):
        self.name = name
        self.detector = detector
        self.pollRate = pollRate
        self.reserveCheck = reserveCheck
        self.reserveDevice = reserveDevice
        self.releaseDevice = releaseDevice
        self.reservationTimeout = reservationTimeout
        self.ownsDevice = False

    @staticmethod
    def serviceDeviceHandling():
        DeviceType.detectDevices()


    @staticmethod
    def addDeviceTypeToDetect(dev):
        DeviceType._deviceTypes.append(dev)

    @staticmethod
    def detectDevices():
        for devType in DeviceType._deviceTypes:
            for dev in devType.detector():
                if type(dev) != Device:
                    raise Exception("All detected devices need to be Device()")
                print(f"detected a {devType.name} device")
                if devType.reserveDevice is not None:
                    DeviceType._visableDevices.append(dev)
                else:
                    DeviceType._reservedDevices.append(dev)

    @staticmethod
    def getVisableDevices():
        return DeviceType._visableDevices

    @staticmethod
    def getReservedDevices():
        return DeviceType._reservedDevices
