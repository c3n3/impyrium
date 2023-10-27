# import the base aitpi
from aitpi.src import aitpi
from aitpi.src.aitpi import router

import os

# In order to receive messages can either make an object with a consume(message) function
# or just provide a function `def consume(message)`
def run_py(message):
    if (message.event == aitpi.BUTTON_PRESS and message.attributes['type'] == 'python_commands'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
        print("Running file")

router.addConsumer([1], run_py)

# We must first initialize our command registry before we can start getting input
aitpi.addRegistry("test_json/registry.json", "test_json/foldered_commands.json")

# Once we initialize our system, all interrupt based commands can be sent imediately.
# Therefore, make sure you are ready to handle any input in your functions before calling this.
aitpi.initInput("test_json/input.json")

# aitpi.addInput('<ctrl>+9')

# aitpi.changeInputRegLink('<ctrl>+9', 'run.py')

# For synchronous input (not interrupt based) using the 'key_input' input mechanism is desireable
# You can setup a custom progromatic form of input using this (If it is good enough, add it to AITPI!)
while (True):
    aitpi.takeInput(input())
