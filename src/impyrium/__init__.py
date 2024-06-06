import sys

from . import control
from . import device_thread
from . import main_menu
from . import default_files

from PyQt6.QtWidgets import QApplication
from .aitpi.src.aitpi import router
from .aitpi.src import aitpi

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

    control.init()
    device_thread.start()

    default_files.writeFiles(_tempFolder, False)


def start(logo=None):
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

    aitpi.addRegistry(_registryFile, _folderCommands)
    aitpi.initInput(_inputsFile)

    app = QApplication(sys.argv)

    window = main_menu.MainWindow(logo)
    window.show()
    app.exec()

def getTempFolder():
    global _tempFolder
    return _tempFolder
