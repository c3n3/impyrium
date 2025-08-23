import sys

from . import control
from . import device_thread
from . import main_menu
from . import default_files

from PySide6.QtWidgets import QApplication, QWidget
from .aitpi.src.aitpi import router
from .aitpi.src import aitpi
from .main_menu import MainWindow
from . import main_menu
from . import worker_thread


import os
import json

_tempFolder = None
_inputsFile = None
_registryFile = None
_folderCommands = None
_app = QApplication(sys.argv)


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
    main_menu.init()

def start(logo=None, title=None, superWindow: QWidget = None):
    global _inputsFile
    global _registryFile
    global _folderCommands
    global _app

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

    window = main_menu.MainWindow(logo, title, superWindow)

    window.show()
    _app.exec()
    device_thread.stop()
    for thread in worker_thread.WorkerThread._allWorkers:
        thread.stop()

def getTempFolder():
    global _tempFolder
    return _tempFolder
