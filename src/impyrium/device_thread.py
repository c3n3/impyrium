from PyQt6.QtCore import QThread
import sched
import time

worker_ = None

class DeviceThread(QThread):
    def __init__(self):
        super().__init__()
        self.scheduler = sched.scheduler(time.time,
                                    time.sleep)

    def run(self):
        while (True):
            self.scheduler.run()
            time.sleep(0.5)

def scheduleItem(delay, fun, arguments=(), priority=0):
    return worker_.scheduler.enter(delay, priority, fun, arguments)

def start():
    global worker_
    if worker_ == None:
        worker_ = DeviceThread()
    worker_.start()

