# import the base aitpi
from aitpi.src import aitpi
from aitpi.src.aitpi import router

import os

def run_py(message):
    if (message.event == aitpi.BUTTON_PRESS and message.attributes['type'] == 'python_commands'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
        print("Running file")

router.addConsumer([1], run_py)
aitpi.addRegistry("test_json/registry.json", "test_json/foldered_commands.json")
aitpi.initInput("test_json/input.json")

while (True):
    aitpi.takeInput(input())
