import sys
import time

from .popups.status_sidebar import StatusSidebar

from .aitpi.src.aitpi import router
from .aitpi.src import aitpi

from .aitpi_signal import AitpiSignalExecutor

from . import helpers
from .aitpi_signal import AitpiSignal
from . import signals
from .thread_safe_queue import ThreadSafeQueue
from .aitpi_widget import Aitpi
from . import device_thread
from .widgets.main_impyrium import MainImpyrium
import os
from PySide6 import QtGui

from .popups import build_a_popup

from . import common_css
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QScrollArea,
    QComboBox,
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QHBoxLayout,
    QSizePolicy
)

from .popups.single_select_popup import SingleSelectPopup

def getFileConsumer(msg):
    fun = msg['fun']
    directory = msg['directory']
    types = msg['types']
    file = helpers.getFileFromDialog(types, directory)
    fun(file)

def selectItemConsumer(msg):
    fun = msg['fun']
    items = msg['items']
    name = msg['name']
    devices = msg['devices']
    dialog = SingleSelectPopup(fun, name, items, devices)
    devs, res = dialog.popUp()
    fun((devs, res))

def buildPopupConsumer(msg):
    fun = msg['fun']
    name = msg['name']
    components = msg['components']
    devices = msg['devices']
    dialog = build_a_popup.BuildAPopup(fun, name, devices, components)
    devs, res = dialog.popUp()
    fun((devs, res))

def addStatusEntry(msg):
    action, text = msg
    if action == "REMOVE":
        StatusSidebar.removeEntry(text)
    elif action == "ADD":
        StatusSidebar.addEntry(text)

def getScriptPath():
    return os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")

def printAllOfType(item, t):
    for d in dir(item):
        if (type(item.__getattribute__(d)) == t):
            print(d)

def init():
    router.addConsumer([signals.GET_FILE], getFileConsumer)
    router.addConsumer([signals.SELECT_ITEM], selectItemConsumer)
    router.addConsumer([signals.ADD_SIDEBAR_STATUS_ENTRY], addStatusEntry)
    router.addConsumer([signals.CUSTOM_POPUP], buildPopupConsumer)

class SuperWindow(QWidget):
    def setMainImpyrium(self, mainImpyrium: MainImpyrium):
        raise NotImplementedError("This method should be implemented in the subclass")

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self, logo, title, superWindow: SuperWindow = None):
        super().__init__()
        if title is None:
            self.setWindowTitle("Impyrium")
        else:
            self.setWindowTitle(title)
        self.setStyleSheet(common_css.MAIN_STYLE)
        self.setMinimumSize(800, 500)
        self.fileCallback = None
        self.selectedDevice = None
        self.signalExec = AitpiSignalExecutor()
        self.signalExec.start()

        # None registry is the control box
        commands = aitpi.getCommandsByRegistry(None)
        categories = set()
        for c in commands:
            categories.add(c['id'])

        if logo is not None:
            self.setWindowIcon(QtGui.QIcon(logo()))
        else:
            self.setWindowIcon(QtGui.QIcon(helpers.getImageForPyQt("logo")))

        if superWindow is not None:
            self.mainImpyrium = MainImpyrium(categories, superWindow)
            superWindow.setMainImpyrium(self.mainImpyrium)
            superWindow.setParent(self)
            self.setCentralWidget(superWindow)
        else:
            self.mainImpyrium = MainImpyrium(categories, self)
            # Ensure the widget expands to fill the window
            self.mainImpyrium.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.setCentralWidget(self.mainImpyrium)

        self.isLinux = sys.platform.startswith('linux')


    def keyPressEvent(self, event):
        if self.isLinux:
            aitpi.pyqt6KeyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.isLinux:
            aitpi.pyqt6KeyReleaseEvent(event)

    def closeEvent(self, event):
        self.end()
        event.accept()

    def close(self):
        self.end()
        super().close()

    def end(self):
        StatusSidebar.stop()
