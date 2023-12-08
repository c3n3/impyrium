import time
from src import impyrium
from src.impyrium.aitpi.src import aitpi
from src.impyrium import control
from src.impyrium.aitpi.src.aitpi.input_initializer import TerminalKeyInput
import os

TerminalKeyInput.shouldSpawnThreads(True)
# TerminalKeyInput.setDebug(True)


def detect():
    return [control.Device(0, "Usb device")]

def reserve(device):
    return

def release(device):
    return


def otherDevices():
    ret = []
    for i in range(2):
        ret.append(control.Device(f"{i} Other", "Other device"))
    return ret

    
impyrium.init("./test_json/inputs.json", "./test_json/registry.json", "./test_json/folder_commands.json")

# Add all controls and devices

def doSomething(ctrl, event, devlist):
    print("Got", ctrl.name, "with", event, devlist)

control.registerControl(control.ControlButton("Category1", "Control1", doSomething))
control.registerControl(control.ControlButton("Category1", "Control2", doSomething))
control.registerControl(control.ControlButton("Category1", "Control3", doSomething))
control.registerControl(control.ControlFile("Category1", "File", doSomething))
control.registerControl(control.ControlButton("Category2", "Control4", doSomething))
control.registerControl(control.ControlSlider("Category2", "Control5", doSomething, sliderRange=control.RangeValue(0, 100, 0.5)))
control.registerControl(control.ControlSlider("Category2", "Control6", doSomething, sliderRange=control.RangeValue(0, 100, 0.5)))
control.registerControl(control.ControlSlider("Category3", "Control7", doSomething, sliderRange=control.RangeValue(-100, 100, 0.5)))
control.registerControl(control.ControlSlider("Category3", "Control8", doSomething, sliderRange=control.RangeValue(0, 100, 0.5)))

usbDevices = control.DeviceType(
    "Usb device",
    detector=detect,
    releaseDeviceFun=release,
    reserveDeviceFun=reserve,
    autoReservationTimeout=5,
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
