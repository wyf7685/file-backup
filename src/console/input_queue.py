import asyncio
import time
from threading import Thread
from typing import Optional

from src.utils import Queue


class InputQueue(object):
    _queue: Queue[str]
    _running: bool
    _thread: Thread

    def _run(self) -> None:
        while self._running:
            try:
                self._queue.put(input())
            except EOFError:
                self._running = False
            time.sleep(0.05)

    def start(self) -> None:
        self._queue = Queue(0)
        self._running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    async def get(self) -> Optional[str]:
        while self._running:
            if not self._queue.empty():
                return self._queue.get()
            await asyncio.sleep(0.05)
