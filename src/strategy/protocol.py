from __future__ import annotations

from typing import Protocol, runtime_checkable

import loguru

from src.models import BackupRecord


@runtime_checkable
class StrategyProtocol(Protocol):
    logger: loguru.Logger

    async def make_backup(self) -> None: ...

    async def make_recovery(self, record: BackupRecord) -> None: ...
