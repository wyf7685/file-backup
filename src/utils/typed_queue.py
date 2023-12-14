from queue import Queue as _Queue
from typing import Generic, TypeVar

from typing_extensions import override

_T = TypeVar("_T")


class Queue(_Queue, Generic[_T]):
    """
    Same as `queue.Queue`, but added generic support

    e.g.:
    >>> que: Queue[str] = Queue()
    """

    @override
    def put(self, item: _T, block: bool = True, timeout: float | None = None) -> None:
        return super().put(item, block, timeout)

    @override
    def get(self, block: bool = True, timeout: float | None = None) -> _T:
        return super().get(block, timeout)

    @override
    def put_nowait(self, item: _T) -> None:
        return super().put_nowait(item)

    @override
    def get_nowait(self) -> _T:
        return super().get_nowait()
