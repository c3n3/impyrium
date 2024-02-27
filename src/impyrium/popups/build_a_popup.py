import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import QTimer
from ..widgets.item_scroll_view import ItemScrollView
from ..inputless_combo import InputlessCombo
from ..aitpi.src import aitpi
from ..aitpi_signal import AitpiSignal
import pynput
from .popup import Popup

class Input():
    def __init__(self) -> None:
        self.value = None
        self.widget = None

    def getWidget(self):
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

    def setValue(self, value):
        pass

class SliderInput(Input):
    def __init__(self, valueChangedFun) -> None:
        self.valueChangedFun = valueChangedFun
        self.widget = #

class TextInput(Input):
    def __init__(self, valueChangedFun=None):
        self.widget = QTextEdit()
        self.value = ""
        self.valueChangedFun = valueChangedFun
        self.widget.textChanged.connect(self.valueChanged)

    def valueChanged(self):
        self.value = self.widget.toPlainText()
        if self.valueChangedFun is not None:
            self.valueChangedFun(self.value)

    def setValue(self, value):
        self.widget.setText(value)
        self.value = value

class TextOutput(QLabel):
    pass

class ComboInput():
    pass

class BuildAPopup(Popup):
    def __init__(self, doneFun, name, devices, components, parent: QWidget = None):
        super().__init__(parent)
        self.doneFun = doneFun
        self.mainLayout = QVBoxLayout(self)
        self.instructions = QLabel(self)
        self.name = name
        self.devices = devices
        self.instructions.setText(name)
        self.setWindowTitle(self.name)
        self.setMinimumWidth(800)

        self.device = "All"
        self.devcombo = InputlessCombo(self)
        self.devcombo.addItem("All")
        for dev in devices:
            self.devcombo.addItem(dev)
        self.devcombo.currentIndexChanged.connect(self.changeDev)
        self.devcomboLabel = QLabel("Select Device")
        self.devcomboLabel.setBuddy(self.devcombo)

        self.mainLayout.addWidget(self.instructions)
        self.mainLayout.addWidget(self.devcomboLabel)
        self.mainLayout.addWidget(self.devcombo)

        self.components = components
        for name, item in self.components.items():
            temp = QWidget(self)
            lay = QHBoxLayout(self)
            widget = item.getWidget()
            label = QLabel(self)
            label.setText(name)
            lay.addWidget(label)
            lay.addWidget(widget)
            temp.setLayout(lay)
            self.mainLayout.addWidget(temp)

    # Required to allow us to handle on a QT thread
    def consume(self, msg):
        if msg == "CLOSE":
            self.close()

    def handleKeyEvent(self, char, event):
        if event == aitpi.BUTTON_PRESS:
            if char == pynput.keyboard.Key.enter:
                self.msgQt("CLOSE")

    def changeDev(self, dev):
        self.device = dev

    def popUp(self):
        super().exec()
        if self.index is not None:
            return self.items[self.index]
        return None

if __name__ == '__main__':
    class TestApp(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")
            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)
            self.timer=QTimer()
            self.timer.timeout.connect(self.signalTimer)
            self.timer.setInterval(100)
            self.timer.start()

        def signalTimer(self):
            AitpiSignal.run()

        def addInput(self, t, item):
            print(t, item)

        def button_clicked(self, s):
            dlg = BuildAPopup(self.addInput, "Something", ["one", "two"], {"Something": TextInput(print), "Else": TextInput()}, self)
            dlg.exec()

    app = QApplication(sys.argv)

    aitpi.TerminalKeyInput.startKeyListener()

    window = TestApp()
    window.show()

    app.exec()