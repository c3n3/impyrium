# Vision
This folder contains example APIs to provide a vision for how this package is going to work.

## Purpose
Impyrium is meant to be a control mechanism for custom devices attached to a computer.
It will provide the user with a GUI and keyboard shortcut integration for control of their
devices. The user simply needs to provide a list of controls and functions to facilitate those
controls.

I want to create this interface to mostly use JSON as the means of configuration. This format
is human readable, simple, and provides an easy programming interface.
 - Maybe just using a python API is better than JSON here. Since the GUI is tied into this module
   it probably does not need to be in json format. This means an API for adding commands is needed.
