import time
from src import impyrium
from src.impyrium.aitpi.src import aitpi
from src.impyrium import control
from src.impyrium.aitpi.src.aitpi.input_initializer import TerminalKeyInput
import os

TerminalKeyInput.shouldSpawnThreads(True)
# TerminalKeyInput.setDebug(True)


def doSomething(ctrl, event, devlist):
    print("Sent", ctrl.name, "with", event)

start = time.time()
def detectUsbs():
    seconds = time.time() - start
    seconds = min(10, int(seconds / 5))
    ret = []
    for i in range(seconds):
        ret.append(control.Device(i))
    return ret

    
impyrium.init("./test_json/inputs.json", "./test_json/registry.json", "./test_json/folder_commands.json")

# Add all controls and devices

control.registerControl(control.Control("Category1", "Control1", control.CONTROL_BUTTON, doSomething))
control.registerControl(control.Control("Category1", "Control2", control.CONTROL_BUTTON, doSomething))
control.registerControl(control.Control("Category1", "Control3", control.CONTROL_BUTTON, doSomething))
control.registerControl(control.Control("Category2", "Control4", control.CONTROL_BUTTON, doSomething))
control.registerControl(control.Control("Category2", "Control5", control.CONTROL_SLIDER, doSomething))
control.registerControl(control.Control("Category2", "Control6", control.CONTROL_SLIDER, doSomething))
control.registerControl(control.Control("Category3", "Control7", control.CONTROL_SLIDER, doSomething))
control.registerControl(control.Control("Category3", "Control8", control.CONTROL_SLIDER, doSomething))
control.registerDeviceType(control.DeviceType("Usb device", detectUsbs, releaseDeviceFun=lambda x: print("Release", x)))

def run_py(message):
    if (message.event == aitpi.BUTTON_PRESS and message.attributes['id'] == 'python_commands'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
    elif (message.event in aitpi.ENCODER_VALUES and message.attributes['id'] == 'python_encoders'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']} {message.event}")

aitpi.router.addConsumer(['python_commands', 'python_encoders'], run_py)

impyrium.start()

aitpi.shutdown()
