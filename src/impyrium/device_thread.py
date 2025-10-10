from PySide6.QtCore import QThread
import sched
import time
import traceback

worker_ = None
stop_ = False

class DeviceThread(QThread):
    def __init__(self):
        super().__init__()
        self.scheduler = sched.scheduler(time.time,
                                    time.sleep)

    def run(self):
        while (not stop_):
            try:
                self.scheduler.run()
            except Exception as e:
                print(traceback.format_exc())
                print("DEVICE THREAD ERROR:", e)
            time.sleep(0.5)

def scheduleItem(delay, fun, arguments=(), priority=0):
    return worker_.scheduler.enter(delay, priority, fun, arguments)

def cancel(event):
    return worker_.scheduler.cancel(event)

def stop():
    global worker_
    global stop_
    stop_ = True
    if worker_ is not None:
        time.sleep(0.25)
        worker_.terminate()
        worker_ = None

def start():
    global worker_
    if worker_ == None:
        worker_ = DeviceThread()
    worker_.start()
