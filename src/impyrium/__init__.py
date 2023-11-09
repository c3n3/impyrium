import sys

from . import control
from . import device_thread
from . import main_menu

from aitpi import router
import aitpi

_inputsFile = None
_registryFile = None
_folderCommands = None

def init(inputsFile, registryFile, folderCommands=None):
    global _inputsFile
    global _registryFile
    global _folderCommands
    _inputsFile = inputsFile
    _registryFile = registryFile
    _folderCommands = folderCommands

    control.init()
    device_thread.start()

def start():
    global _inputsFile
    global _registryFile
    global _folderCommands

    aitpi.addRegistry(_registryFile, _folderCommands)
    aitpi.initInput(_inputsFile)

    app = main_menu.QApplication(sys.argv)

    window = main_menu.MainWindow()
    window.show()


    app.exec()