import asyncio
import time
from threading import Thread
from typing import Optional

from src.utils import Queue


class InputQueue(object):
    _queue: Queue[str] = Queue(0)
    _thread: Thread
    _running: bool = False
    
    def start(self):
        self._running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while self._running:
            try:
                self._queue.put(input())
            except EOFError:
                self._running = False
            time.sleep(0.05)

    async def get(self) -> Optional[str]:
        while self._running:
            if not self._queue.empty():
                return self._queue.get()
            await asyncio.sleep(0)
