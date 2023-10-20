import asyncio
import time
from threading import Thread

from src.utils import Queue


class InputQueue(object):
    _queue: Queue[str] = Queue(0)
    _thread: Thread

    def __init__(self) -> None:
        pass
    
    def start(self):
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while True:
            try:
                self._queue.put(input())
            except EOFError:
                break
            time.sleep(0.05)

    async def get(self) -> str:
        while True:
            if not self._queue.empty():
                return self._queue.get()
            await asyncio.sleep(0)
