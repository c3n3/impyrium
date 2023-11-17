from PyQt6.QtCore import QThread
import sched
import time
import traceback

worker_ = None

class DeviceThread(QThread):
    def __init__(self):
        super().__init__()
        self.scheduler = sched.scheduler(time.time,
                                    time.sleep)

    def run(self):
        while (True):
            try:
                self.scheduler.run()
            except Exception as e:
                print(traceback.format_exc())
                print("DEVICE THREAD ERROR:", e)
            time.sleep(0.5)

def scheduleItem(delay, fun, arguments=(), priority=0):
    return worker_.scheduler.enter(delay, priority, fun, arguments)

def start():
    global worker_
    if worker_ == None:
        worker_ = DeviceThread()
    worker_.start()

