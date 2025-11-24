import py_global_shortcuts as pygs
from . import control
from . import device_thread
from . import main_menu
from . import default_files
from . import main_menu
from . import worker_thread


import os
import json

PYGS_APPNAME = "impyrium_app"
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

    pygs.init(PYGS_APPNAME, cache_dir=_tempFolder)

    device_thread.start()

    default_files.writeFiles(_tempFolder, False)

def start():
    global _inputsFile
    global _registryFile
    global _folderCommands

    defaultInputsFile = f"{_tempFolder}/inputs.json"
    if _inputsFile is None:
        _inputsFile = defaultInputsFile
        if not os.path.exists(defaultInputsFile):
            f = open(defaultInputsFile, "w")
            json.dump([], f)
            f.close()

    defaultRegistryFile = f"{_tempFolder}/registry.json"
    if _registryFile is None:
        _registryFile = defaultRegistryFile
        if not os.path.exists(defaultRegistryFile):
            f = open(defaultRegistryFile, "w")
            json.dump([], f)
            f.close()

def stop():
    device_thread.stop()
    for thread in worker_thread.WorkerThread._allWorkers:
        thread.stop()

def getTempFolder():
    global _tempFolder
    return _tempFolder
