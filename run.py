import time
from src import impyrium
from src.impyrium.aitpi.src import aitpi
from src.impyrium import control
from src.impyrium.aitpi.src.aitpi.input_initializer import TerminalKeyInput
import os

TerminalKeyInput.shouldSpawnThreads(True)
# TerminalKeyInput.setDebug(True)


def doSomething(ctrl, event, devlist, arguments=None):
    print("Sent", ctrl.name, "with", event, devlist, arguments)

start = time.time()
def detectUsbs():
    ret = []
    for i in range(2):
        ret.append(control.Device(i, "Usb device"))
    return ret

def otherDevices():
    ret = []
    for i in range(2):
        ret.append(control.Device(f"{i} Other", "Other device"))
    return ret

    
impyrium.init("./test_json/inputs.json", "./test_json/registry.json", "./test_json/folder_commands.json")

# Add all controls and devices

control.registerControl(control.Control("Category1", "Control1", control.ControlButton(), doSomething))
control.registerControl(control.Control("Category1", "Control2", control.ControlButton(), doSomething))
control.registerControl(control.Control("Category1", "Control3", control.ControlButton(), doSomething))
control.registerControl(control.Control("Category2", "Control4", control.ControlButton(), doSomething))
control.registerControl(control.Control("Category2", "Control5", control.ControlSlider(0, 100, 0.5), doSomething))
control.registerControl(control.Control("Category2", "Control6", control.ControlSlider(0, 100, 0.5), doSomething))
control.registerControl(control.Control("Category3", "Control7", control.ControlSlider(-100, 100, 0.5), doSomething))
control.registerControl(control.Control("Category3", "Control8", control.ControlSlider(0, 100, 0.5), doSomething))

usbDevices = control.DeviceType(
    "Usb device",
    detector=detectUsbs,
    controlCategories=["Category1"]
)

otherDevs = control.DeviceType(
    "Other device",
    detector=otherDevices,
    controlCategories=["Category3"]
)

control.registerDeviceType(usbDevices)
control.registerDeviceType(otherDevs)

def run_py(message, event, devList):
    if (message.event == aitpi.BUTTON_PRESS and message.attributes['id'] == 'python_commands'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
    elif (message.event in aitpi.ENCODER_VALUES and message.attributes['id'] == 'python_encoders'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']} {message.event}")

aitpi.router.addConsumer(['python_commands', 'python_encoders'], run_py)

impyrium.start()

aitpi.shutdown()
