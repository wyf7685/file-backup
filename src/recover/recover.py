from src.models import BackupConfig, BackupRecord
from src.strategy import StrategyProtocol, get_strategy


class Recover(object):
    @classmethod
    async def create(cls, config: BackupConfig):
        strategy = get_strategy(config.mode)
        cls = type("MixedRecover", (strategy, cls), {})
        self = await cls._create(config)
        await self.prepare(miss_ok=False)
        return self

    async def apply(self, record: BackupRecord) -> None:
        assert isinstance(self, StrategyProtocol)
        await self.make_recovery(record)
