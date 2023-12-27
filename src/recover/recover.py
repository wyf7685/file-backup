from src.models import BackupConfig, BackupRecord
from src.strategy import StrategyProtocol, get_strategy
from src.utils import Style


class Recover(object):
    @classmethod
    async def create(cls, config: BackupConfig):
        strategy = get_strategy(config.mode)
        MixedRecover = type("MixedRecover", (strategy, cls), {})
        self = await MixedRecover.init(config)
        await self.prepare(miss_ok=False)
        self.logger.success(f"{Style.GREEN("Recover")} [{Style.CYAN(config.name)}] 初始化成功")
        return self

    async def apply(self, record: BackupRecord) -> None:
        assert isinstance(self, StrategyProtocol)
        await self.make_recovery(record)
