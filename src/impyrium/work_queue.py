# Copyright 2025 by Garmin Ltd. or its subsidiaries.
from impyrium.thread_safe_queue import ThreadSafeQueue
from typing import Callable
from PySide6.QtCore import QTimer
import time
import threading
from typing import TypeVar, List

T = TypeVar('T')

class SortedList(List[T]):
    def __init__(self, list: List[T]) -> None:
        for item in list:
            self.insert(item)

    def insert(self, item: T):
        insert = 0
        for i in range(len(self)):
            insert = i
            if item < self[i]:
                break
            if item > self[i] and i == len(self) - 1:
                insert = len(self)
        super().insert(insert, item)

class WorkItem():
    def __init__(self, exec: Callable[[], None], execTime: int = 0) -> None:
        self.exec = exec
        self.timetoexec = execTime + int(time.time() * 1000)

    def __gt__(self, other: "WorkItem"):
        return self.timetoexec > other.timetoexec

    def __lt__(self, other: "WorkItem"):
        return self.timetoexec < other.timetoexec

    def __eq__(self, other: "WorkItem"):
        return self.timetoexec == other.timetoexec

    def __hash__(self):
        return hash((self.exec, self.timetoexec))

class WorkQueue():
    allItems: SortedList[WorkItem] = SortedList([])
    lock = threading.Lock()

    @staticmethod
    def cancel(itemId: int):
        if itemId is None:
            return
        WorkQueue.lock.acquire()
        for i in range(len(WorkQueue.allItems)):
            if id(WorkQueue.allItems[i]) == itemId:
                WorkQueue.allItems.pop(i)
                break
        WorkQueue.lock.release()

    @staticmethod
    def schedule(fun: Callable[[], None], execTime: int = 0) -> int:
        WorkQueue.lock.acquire()
        item = WorkItem(fun, execTime)
        WorkQueue.allItems.insert(item)
        WorkQueue.lock.release()
        return id(item)

    @staticmethod
    def run():
        now = int(time.time() * 1000)
        itemToExec = []
        WorkQueue.lock.acquire()
        while len(WorkQueue.allItems) > 0 and WorkQueue.allItems[0].timetoexec <= now:
            item = WorkQueue.allItems.pop(0)
            if item is not None:
                itemToExec.append(item)
        WorkQueue.lock.release()
        for item in itemToExec:
            item.exec()

def cancel(itemId: int):
    return WorkQueue.cancel(itemId)

def schedule(fun: Callable[[], None], execTime: int = 0):
    return WorkQueue.schedule(fun, execTime)

class WorkQueueExecutor():
    def __init__(self) -> None:
        self.timer=QTimer()
        self.timer.timeout.connect(self.signalTimer)
        self.timer.setInterval(10)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def signalTimer(self):
        WorkQueue.run()
