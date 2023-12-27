from typing import TYPE_CHECKING, Optional, Protocol, Self, runtime_checkable

from src.models import BackupConfig, BackupRecord

if TYPE_CHECKING:
    from src.log import Logger


@runtime_checkable
class StrategyProtocol(Protocol):
    logger: "Logger"

    async def make_backup(self) -> None:
        ...

    async def make_recovery(self, record: BackupRecord) -> None:
        ...
