from PySide6.QtCore import QThread
import sched
import time

class WorkerThread(QThread):
    def __init__(self, sleepTime=0.1):
        super().__init__()
        self.scheduler = sched.scheduler(time.time,
                                    time.sleep)
        self.sleepTime = sleepTime

    def run(self):
        while (True):
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
