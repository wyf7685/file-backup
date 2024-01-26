import typing as _t

from src.const import BackupMode

from .protocol import StrategyProtocol as StrategyProtocol
from .strategy import AbstractStrategy as Strategy


def get_strategy(mode: BackupMode) -> _t.Type[Strategy]:
    from importlib import import_module

    module = import_module(f".{mode}", __package__)
    backend_cls = getattr(module, "Strategy", Strategy)
    assert issubclass(backend_cls, Strategy)
    return backend_cls
