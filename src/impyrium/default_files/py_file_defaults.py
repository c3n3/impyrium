from .default_file import DefaultFile
from . import defaults

runFile = DefaultFile(f"run.py",
f"""\
import time
import impyrium
import aitpi
from impyrium import control
import os

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


impyrium.init("{defaults.JSON_FOLDER}/{defaults.INPUTS_FILE}", "{defaults.JSON_FOLDER}/{defaults.REGISTRY_FILE}", "{defaults.JSON_FOLDER}/{defaults.FOLDER_COMMANDS_FILE}")

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
        os.system(f"python3 {{message.attributes['path']}}/{{message.attributes['name']}}")
    elif (message.event in aitpi.ENCODER_VALUES and message.attributes['id'] == 'python_encoders'):
        os.system(f"python3 {{message.attributes['path']}}/{{message.attributes['name']}} {{message.event}}")

aitpi.router.addConsumer(['python_commands', 'python_encoders'], run_py)

impyrium.start()

"""
)

test0 = DefaultFile(f"{defaults.FOLDER_COMMANDS_TEST_COMMANDS_PATH}/test0.py",
"""
print('The test file 0 has run')
"""
)

test1 = DefaultFile(f"{defaults.FOLDER_COMMANDS_TEST_COMMANDS_PATH}/test1.py",
"""
print('The test file 1 has run')
"""
)

encoder0 = DefaultFile(f"{defaults.FOLDER_COMMANDS_TEST_ENCODERS_PATH}/encoder0.py",
"""
import sys
print('Encoder 0', sys.argv[1])
"""
)

encoder1 = DefaultFile(f"{defaults.FOLDER_COMMANDS_TEST_ENCODERS_PATH}/encoder1.py",
"""
import sys
print('Encoder 1', sys.argv[1])
"""
)
