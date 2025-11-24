from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSlider
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, Qt
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
from .. import common_css
from .popup import Popup
import os

def getScriptPath():
    return f'{os.path.dirname(os.path.realpath(__file__)).replace(os.path.basename(__file__), "")}'

class DeviceInfoPopup(Popup):
    def __init__(self, name, info, logo=None, parent: QWidget = None):
        super().__init__(parent)
        self.shouldReturnValue = False
        self.setStyleSheet(common_css.MAIN_STYLE)
        self.focusIdx = 0
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.name = name
        self.instructions.setText(name)
        self.setWindowTitle(self.name)
        # self.setMinimumWidth(100)


        text = ""
        for key, value in info.items():
            text += f"{str(key)}: {str(value)}\n"
        self.instructions.setText(text)
        self.instructions.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse);
        self.mainLayout.addWidget(self.instructions)

        if logo is not None:
            label = QLabel(self)
            pixmap = QPixmap(logo).scaledToWidth(50)
            label.setPixmap(pixmap)
            self.mainLayout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
