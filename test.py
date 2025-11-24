
import sys
import time

from src.impyrium.worker_thread import WorkerThread
import os
import threading
import typing
from src.impyrium.thread_safe_queue import ThreadSafeQueue

from PySide6.QtCore import Qt, pyqtBoundSignal, pyqtSignal, pyqtSlot, QTimer
from PySide6.QtWidgets import (
    QScrollArea,
    QFileDialog,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QHBoxLayout,
)

class QueueItem():
    def __init__(self, fun, arg) -> None:
        self.fun = fun
        self.arg = arg

    def run(self):
        self.fun(self.arg)


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impyrium")
        self.setMinimumSize(800, 500)
        self.fileCallback = None

        # None registry is the control box
        mainWidget = QPushButton()

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(mainWidget)

        self.timer=QTimer()
        self.timer.timeout.connect(self.something)
        self.timer.setInterval(100)
        self.timer.start()
        self.queue = ThreadSafeQueue()

    def something(self):
        value = self.queue.pop()
        while (value != None):
            value.run()
            value = self.queue.pop()
            print("Ran queue item")

worker = WorkerThread()

worker.start()


app = QApplication(sys.argv)

window = MainWindow()

def runAlways():
    window.queue.put(QueueItem(lambda arg: print("Something happened"), None))
    worker.scheduleItem(1, runAlways)

runAlways()

window.show()

app.exec()
