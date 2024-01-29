from src.config import BackupConfig
from src.const.exceptions import StopOperation
from src.models import BackupRecord
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
        with self.logger.catch():
            try:
                await self.make_recovery(record)
                self.logger.success(f"备份 [{Style.CYAN(record.uuid)}] 恢复完成!")
            except StopOperation as e:
                # 中止恢复
                self.logger.warning(f"恢复错误: {Style.RED(e)}")
            except Exception as e:
                self.logger.exception(f"未知错误: {Style.RED(e)}")
                self.logger.warning("中止恢复...")
