import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6 import QtGui
from ..aitpi.src import aitpi
from ..aitpi_signal import AitpiSignal, AitpiSignalExecutor
from .popup import Popup
from enum import Enum

statusBar = None

class StatusPlace():
    TOP_BOTTOM_BIT = 0x0001
    TOP            = TOP_BOTTOM_BIT
    BOTTOM         = 0x0000

    LEFT_RIGHT_BIT = 0x0002
    LEFT           = LEFT_RIGHT_BIT
    RIGHT          = 0x0000

    @staticmethod
    def isTop(num):
        return (num & StatusPlace.TOP_BOTTOM_BIT) == StatusPlace.TOP

    @staticmethod
    def isBottom(num):
        return (num & StatusPlace.TOP_BOTTOM_BIT) == StatusPlace.BOTTOM

    @staticmethod
    def isLeft(num):
        return (num & StatusPlace.LEFT_RIGHT_BIT) == StatusPlace.LEFT

    @staticmethod
    def isRight(num):
        return (num & StatusPlace.LEFT_RIGHT_BIT) == StatusPlace.RIGHT

class StatusSidebar(Popup):
    count_ = 0

    enabled_ = True

    currentBar_ = None

    def __init__(self, location = (StatusPlace.TOP | StatusPlace.LEFT), parent=None) -> None:
        StatusSidebar.currentBar_ : StatusSidebar
        self.location = location
        super().__init__(parent)
        if StatusSidebar.count_ == 1:
            return
        StatusSidebar.count_ += 1
        self.container = QWidget(self)
        self.containerLay = QVBoxLayout()
        self.containerLay.addWidget(self.container)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoChildEventsForParent, True)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.scale = QtGui.QGuiApplication.primaryScreen().devicePixelRatio()
        self.sc = QtGui.QGuiApplication.primaryScreen().size() * self.scale
        self.container.setStyleSheet('QWidget{background-color: rgba(25,0,200,0.25); color: rgba(150,150,150,0.75)}')
        self.mainLayout = QVBoxLayout()
        if StatusPlace.isBottom(self.location):
            self.mainLayout.setDirection(QVBoxLayout.Direction.TopToBottom)
            self.top = self.isTop()
        self.container.setLayout(self.mainLayout)
        self.setLayout(self.containerLay)
        self.widgets = {}
        self.updateLocation()

    def isTop(self):
        if (self.location & StatusPlace.TOP_BOTTOM_BIT) == StatusPlace.TOP:
            pass

    def popUp(self):
        self.show()

    def removeStatusEntry(self, text):
        if text in self.widgets:
            self.mainLayout.removeWidget(self.widgets[text])
            del self.widgets[text]

    def addStatusEntry(self, text, color="rgba(255,255,255,1)"):
        if text in self.widgets:
            self.mainLayout.removeWidget(self.widgets[text])
            del self.widgets[text]

        widget = QLabel(text)
        widget.setStyleSheet(f'QWidget{{ background-color: rgba(255,255,255,0); color: {color} }}')
        if StatusPlace.isBottom(self.location):
            self.mainLayout.insertWidget(0, widget)
        else:
            self.mainLayout.addWidget(widget)
        self.mainLayout.update()
        self.widgets[text] = widget
        # self.updateLocation()

    def updateLocation(self):
        x = self.sc.width()
        y = self.sc.height()
        if StatusPlace.isBottom(self.location):
            y = y - self.container.height()
            print(self.container.height(), y)
        if StatusPlace.isTop(self.location):
            y = 0
        if StatusPlace.isRight(self.location):
            x = x - self.container.width()
        if StatusPlace.isLeft(self.location):
            x = 0
        print(x, y)
        self.move(int(x), int(y))
        self.update()

    def end(self):
        StatusSidebar.count_ -= 1
        super().end()

    @staticmethod
    def start():
        if StatusSidebar.enabled_ and StatusSidebar.currentBar_ is None:
            StatusSidebar.currentBar_ = StatusSidebar()
            StatusSidebar.currentBar_.popUp()


    @staticmethod
    def stop():
        if StatusSidebar.currentBar_ is not None:
            StatusSidebar.currentBar_.close()
            StatusSidebar.currentBar_ = None

    @staticmethod
    def enableStatusBar(value=True):
        if StatusSidebar.enabled_ and StatusSidebar.currentBar_ is not None:
            StatusSidebar.currentBar_.close()
            StatusSidebar.currentBar_ = None
        StatusSidebar.enabled_ = value

    @staticmethod
    def addEntry(text, color="rgba(255,255,255,1)"):
        if not StatusSidebar.enabled_:
            return
        StatusSidebar.start()
        StatusSidebar.currentBar_.addStatusEntry(text, color)

    @staticmethod
    def removeEntry(text):
        if not StatusSidebar.enabled_:
            return
        StatusSidebar.start()
        StatusSidebar.currentBar_.removeStatusEntry(text)
        if len(StatusSidebar.currentBar_.widgets) == 0:
            StatusSidebar.currentBar_.close()
            StatusSidebar.currentBar_= None

if __name__ == '__main__':
    from ..aitpi_signal import AitpiSignalExecutor
    class TestApp(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")
            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)
            self.executor = AitpiSignalExecutor()
            self.executor.start()
            self.dlg = None
            self.flip = True
            self.count = 0

        def signalTimer(self):
            AitpiSignal.run()

        def addInput(self, t, item):
            print(t, item)

        def button_clicked(self, s):
            # if self.flip:
            self.count += 1
            StatusSidebar.addEntry("Something " + str(self.count), "rgba(255,255,255,1)")
            # else:
            #     StatusSidebar.removeEntry("Something")

            self.flip = not self.flip

        def closeEvent(self, event):
            self.end()
            event.accept()

        def close(self):
            self.end()
            super().close()

        def end(self):
            StatusSidebar.stop()

    app = QApplication(sys.argv)

    aitpi.TerminalKeyInput.startKeyListener()

    window = TestApp()
    window.show()

    app.exec()
