import threading

class ThreadSafeQueue():
    def __init__(self) -> None:
        self.items = []
        self.lock = threading.Lock()

    def put(self, item):
        self.lock.acquire()
        self.items.append(item)
        self.lock.release()

    def count(self, item):
        ret = 0
        self.lock.acquire()
        ret = len(self.items)
        self.lock.release()
        return ret

    def pop(self):
        ret = None
        self.lock.acquire()
        if (len(self.items) > 0):
            ret = self.items.pop(0)
        self.lock.release()
        return ret
