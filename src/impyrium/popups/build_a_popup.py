import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QSlider
from PySide6.QtCore import QTimer, Qt
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
from .. import common_css
import pynput
from .popup import Popup

class Input():
    def __init__(self) -> None:
        self.value = None
        self.widget = None

    def reset(self):
        self.widget = None

    def getWidget(self, parent=None):
        return self.widget

    def getValue(self):
        return self.value

    def handleKeyEvent(self, char, event):
        pass

    def handleChange(self, newValue):
        self.value = newValue

class Output():
    def __init__(self) -> None:
        self.value = None

    def reset(self):
        self.widget = None

    def getWidget(self, parent=None):
        return self.widget

    def setValue(self, value):
        pass

class TextOutput(Output):
    def __init__(self, value="") -> None:
        self.widget = None
        self.value = value

    def widgetDeath(self):
        self.widget = None

    def getWidget(self, parent=None):
        self.widget = QLabel(parent)
        self.widget.destroyed.connect(self.widgetDeath)
        self.widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.widget.setStyleSheet("text-align: left")
        self.widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse);
        self.setValue(self.value)
        return self.widget

    def setValue(self, value):
        self.value = value
        if self.widget is not None:
            self.widget.setText(self.value)

class SliderInput(Input):
    def __init__(self, range, valueChangedFun=None, styleSheet="") -> None:
        self.valueChangedFun = valueChangedFun
        self.styleSheet = styleSheet
        self.range = range
        self.value = range[0]

    def widgetDeath(self):
        self.widget = None

    def valueChange(self, value):
        self.value = value
        self.valueChangedFun(value)

    def getWidget(self, parent=None):
        self.widget = QSlider(Qt.Orientation.Horizontal, parent)
        self.widget.destroyed.connect(self.widgetDeath)
        self.widget.setMinimum(self.range[0])
        self.widget.setMaximum(self.range[1])
        self.widget.setMinimumHeight(25)
        self.value = self.widget.value()
        if self.valueChangedFun is not None:
            self.widget.valueChanged.connect(self.valueChange)
        self.widget.setStyleSheet(self.styleSheet)
        return self.widget


class TextInput(Input):
    def __init__(self, valueChangedFun=None, styleSheet="", height=100, banned=["\t"]):
        self.value = ""
        self.banned = banned
        self.widget = None
        self.height = height
        self.valueChangedFun = valueChangedFun
        self.styleSheet = styleSheet

    def widgetDeath(self):
        self.widget = None

    def getWidget(self, parent=None):
        self.widget = QTextEdit(parent)
        self.widget.destroyed.connect(self.widgetDeath)
        self.widget.setMaximumHeight(self.height)
        self.widget.textChanged.connect(self.valueChanged)
        self.widget.setStyleSheet(self.styleSheet)
        self.setValue(self.value)
        return self.widget

    def valueChanged(self):
        self.value = self.widget.toPlainText()
        for item in self.banned:
            if item in self.value:
                self.value = self.value.replace(item, "")
                self.setValue(self.value)

        if self.valueChangedFun is not None:
            self.valueChangedFun(self.value)

    def setValue(self, value):
        if self.widget is not None and self.widget:
            self.widget.setText(str(value))
        self.value = str(value)

class NumberInput(TextInput):
    def __init__(self, valueChangedFun=None, styleSheet="", height = 25, max=100000000000):
        self.height = height
        self.max = 100000000000
        self.value = ""
        self.widget = None
        self.valueChangedFun = valueChangedFun
        self.styleSheet = styleSheet
        self.preventRecurse = False

    def valueChanged(self):
        val = self.widget.toPlainText()
        nums = [str(i) for i in range(0, 10)]
        actualValue = ""
        sign = 1
        if len(val) >= 1:
            if val[0] == "-":
                sign = -1
        for char in val:
            if char in nums:
                actualValue += str(char)
        if actualValue != "":
            self.value = int(actualValue) * sign
            if sign == -1:
                actualValue = "-" + actualValue
        elif actualValue == "" and sign == -1:
            actualValue = "-"
        else:
            self.value = None
        if actualValue != val:
            self.widget.setPlainText(actualValue)
        self.valueChangedFun(self.value)
        return self.value

class ComboInput():
    pass

class BuildAPopup(Popup):
    def __init__(self, doneFun, name, devices, components, parent: QWidget = None):
        super().__init__(parent)
        self.shouldReturnValue = False
        self.setStyleSheet(common_css.MAIN_STYLE)
        self.doneFun = doneFun
        self.focusIdx = 0
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.name = name
        self.devices = list(devices)
        self.instructions.setText(name)
        self.setWindowTitle(self.name)
        self.setMinimumWidth(800)
        if len(devices) != 1:
            self.devices = ["All", *devices]
        self.instructions.setText(name)

        self.devIndex = 0
        self.index = None
        self.devcombo = InputlessCombo(self)
        for dev in self.devices:
            if type(dev) is str:
                self.devcombo.addItem(dev)
            else:
                self.devcombo.addItem(dev.getName())
        self.devcombo.currentIndexChanged.connect(self.changeType)
        self.devcomboLabel = QLabel("Select Device")
        self.devcomboLabel.setBuddy(self.devcombo)

        self.mainLayout.addWidget(self.instructions)
        self.mainLayout.addWidget(self.devcomboLabel)
        self.mainLayout.addWidget(self.devcombo)

        self.components = components
        first = None
        tabOrder = []
        for name, item in self.components.items():
            temp = QWidget(self)
            lay = QHBoxLayout()
            widget = item.getWidget(self)
            if issubclass(type(item), Input):
                tabOrder.append(widget)
            if first is None and issubclass(type(item), Input):
                first = widget
                # TODO: We want the first input to be focused automatically
                # So do something here for that
                first.setFocus()

            label = QLabel(self)
            label.setText(name)
            lay.addWidget(label)
            lay.addWidget(widget)
            temp.setLayout(lay)
            self.mainLayout.addWidget(temp)
        tabOrder.append(self.devcombo)

        for i in range(1, len(tabOrder)):
            self.setTabOrder(tabOrder[i-1], tabOrder[i])

    def changeType(self, index):
        self.devIndex = index
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Return:
            self.shouldReturnValue = True
            self.close()
        elif key == Qt.Key.Key_Escape:
            self.shouldReturnValue = False
            self.close()
        elif key == Qt.Key.Key_Tab:
            startFocus = self.focusIdx
            self.focusIdx += 1
            if self.focusIdx >= len(self.components):
                self.focusIdx = 0
            while issubclass(type(self.components[list(self.components.keys())[self.focusIdx]]), Output) and self.focusIdx != startFocus:
                self.focusIdx = (self.focusIdx + 1) % len(self.components)
            self.components[list(self.components.keys())[self.focusIdx]].widget.setFocus()

    def changeDev(self, dev):
        self.device = dev

    def getResults(self):
        ret = {}
        for key, comp in self.components.items():
            if issubclass(type(comp), Input):
                ret[key] = comp.getValue()
        return ret

    def popUp(self):
        super().exec()
        if self.devices[self.devIndex] == "All":
            dev = self.devices[1:]
        else:
            dev = [self.devices[self.devIndex]]

        result = self.getResults()
        return dev, result if self.shouldReturnValue else None
