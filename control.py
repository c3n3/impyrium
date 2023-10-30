from aitpi.src import aitpi
import defaults



CONTROL_BUTTON   = 0
CONTROL_SLIDER     = 1

CONTROL_DIAL     = 1

CONTROL_FILE      = 3

CONTROL_STRING      = 3

CONTROL_DATE      = 3


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

registerControl(Control(0, "Dumb", "nothing", CONTROL_BUTTON, sendSomething))


