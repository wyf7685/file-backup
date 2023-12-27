import typing as _t

from src.const import BackupMode

from .compress import CompressStrategy as CompressStrategy
from .increment import IncrementStrategy as IncrementStrategy
from .protocol import StrategyProtocol as StrategyProtocol
from .strategy import Strategy as Strategy

STRATEGY: _t.Dict[BackupMode, _t.Type[Strategy]] = {
    "compress": CompressStrategy,
    "increment": IncrementStrategy,
}


def get_strategy(mode: BackupMode):
    return STRATEGY[mode]
