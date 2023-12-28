from .aitpi.src.aitpi import router
from .thread_safe_queue import ThreadSafeQueue

class AitpiSignal():
    queue = ThreadSafeQueue()

    @staticmethod
    def send(id, data):
        AitpiSignal.queue.put((id, data))

    @staticmethod
    def run():
        item = AitpiSignal.queue.pop()
        if item is not None:
            id, data = item
            router.send(id, data)

