import py_global_shortcuts as pygs
from . import control
from . import device_thread
from . import main_menu
from . import default_files
from . import main_menu
from . import worker_thread


import os
import json

_tempFolder = None
_inputsFile = None
_registryFile = None
_folderCommands = None

def init(tempFolder, inputsFile=None, registryFile=None, folderCommands=None):
    global _tempFolder
    global _inputsFile
    global _registryFile
    global _folderCommands
    _tempFolder = tempFolder
    _inputsFile = inputsFile
    _registryFile = registryFile
    _folderCommands = folderCommands

    device_thread.start()

    default_files.writeFiles(_tempFolder, False)

def start():
    pass

def stop():
    device_thread.stop()
    for thread in worker_thread.WorkerThread._allWorkers:
        thread.stop()

def getTempFolder():
    global _tempFolder
    return _tempFolder
