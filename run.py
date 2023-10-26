# import the base aitpi
import aitpi

# The postal service allows us to receive messages
from aitpi import router

import os

# In order to receive messages can either make an object with a consume(message) function
# or just provide a function `def consume(message)`
def run_py(message):
    if (message.event == 0 and message.attributes['type'] == 'python_commands'):
        os.system(f"python3 {message.attributes['path']}/{message.attributes['name']}")
        print("Running file")

# Here we add a consumer that will receive commands with ids 0,1,2,3,4, these ids are the sameconsume
# as defined in your registry json file.consume
router.addConsumer([0,1,2,3,4], run_py)

# We must first initialize our command registry before we can start getting input
aitpi.addRegistry("test_json/registry.json", "test_json/foldered_commands.json")

# We can add multiple registries, and do not need the foldered commands
# aitpi.addRegistry("test_json/registry.json")

# Once we initialize our system, all interrupt based commands can be sent imediately.
# Therefore, make sure you are ready to handle any input in your functions before calling this.
aitpi.initInput("test_json/input.json")



# For synchronous input (not interrupt based) using the 'key_input' input mechanism is desireable
# You can setup a custom progromatic form of input using this (If it is good enough, add it to AITPI!)
while (True):
    aitpi.takeInput(input())