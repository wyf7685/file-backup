from queue import Queue as _Queue
from typing import Generic, TypeVar

_T = TypeVar("_T")


class Queue(_Queue, Generic[_T]):
    """
    Same as `queue.Queue`, but added generic support

    e.g.:
    >>> que: Queue[str] = Queue()
    """
    def put(self, item: _T, block: bool = True, timeout: float | None = None) -> None:
        return super().put(item, block, timeout)

    def get(self, block: bool = True, timeout: float | None = None) -> _T:
        return super().get(block, timeout)

    def put_nowait(self, item: _T) -> None:
        return super().put_nowait(item)

    def get_nowait(self) -> _T:
        return super().get_nowait()
    

