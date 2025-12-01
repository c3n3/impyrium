import sys
import time

from typing import Tuple
from . import control
import py_global_shortcuts as pygs
from . import helpers
from . import signals
from .thread_safe_queue import ThreadSafeQueue
from .keybinding_widget import KeybindingWidget
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


def getScriptPath():
    return os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")

def printAllOfType(item, t):
    for d in dir(item):
        if (type(item.__getattribute__(d)) == t):
            print(d)

class SuperWindow(QWidget):
    def __init__(self, minsize: Tuple[int, int] = None):
        super().__init__()
        self.minsize = minsize

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
        if superWindow is not None and superWindow.minsize is not None:
            self.setMinimumSize(*superWindow.minsize)
        else:
            self.setMinimumSize(800, 500)
        self.fileCallback = None
        self.selectedDevice = None

        # None registry is the control box
        commands = pygs.get_binder().get_commands()
        categories = set()
        for c in commands:
            cat, idstr = control.Control.parseId(c.cmd_id)
            categories.add(cat)

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

    def closeEvent(self, event):
        event.accept()

    def close(self):
        super().close()
