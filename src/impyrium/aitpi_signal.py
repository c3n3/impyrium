from .aitpi.src.aitpi import router
from .thread_safe_queue import ThreadSafeQueue
from typing import Callable
from PySide6.QtCore import QTimer

class AitpiSignal():
    queue = ThreadSafeQueue()

    @staticmethod
    def schedule(fun: Callable):
        AitpiSignal.queue.put(fun)

    @staticmethod
    def send(id, data):
        AitpiSignal.queue.put((id, data))

    @staticmethod
    def run():
        item = AitpiSignal.queue.pop()
        if item is not None:
            if isinstance(item, Callable):
                item()
            else:
                id, data = item
                router.send(id, data)


class AitpiSignalExecutor():
    def __init__(self) -> None:
        self.timer=QTimer()
        self.timer.timeout.connect(self.signalTimer)
        self.timer.setInterval(25)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def signalTimer(self):
        AitpiSignal.run()
