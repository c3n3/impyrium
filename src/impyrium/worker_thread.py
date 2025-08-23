from PySide6.QtCore import QThread
import sched
import time
from typing import List

class WorkerThread(QThread):
    _allWorkers: List["WorkerThread"] = []
    def __init__(self, sleepTime=0.1):
        super().__init__()
        self.scheduler = sched.scheduler(time.time,
                                    time.sleep)
        self.sleepTime = sleepTime
        WorkerThread._allWorkers.append(self)
        self.stop_ = False

    def stop(self):
        self.stop_ = True
        time.sleep(0.25)
        self.terminate()

    def run(self):
        while (not self.stop_):
            try:
                self.scheduler.run()
            except Exception as e:
                print(e)
            time.sleep(self.sleepTime)

    def scheduleItem(self, delay, fun, arguments=(), priority=0):
        return self.scheduler.enter(delay, priority, fun, arguments)

    def removeItem(self, item):
        try:
            self.scheduler.cancel(item)
        except:
            pass
