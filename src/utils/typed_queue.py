from queue import Queue as _Queue

from typing import override

class Queue[T](_Queue):
    """
    Same as `queue.Queue`, but added generic support

    e.g.:
    >>> que = Queue[str]()
    """

    @override
    def put(self, item: T, block: bool = True, timeout: float | None = None) -> None:
        return super().put(item, block, timeout)

    @override
    def get(self, block: bool = True, timeout: float | None = None) -> T:
        return super().get(block, timeout)

    @override
    def put_nowait(self, item: T) -> None:
        return super().put_nowait(item)

    @override
    def get_nowait(self) -> T:
        return super().get_nowait()
