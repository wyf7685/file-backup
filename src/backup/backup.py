from src.const.exceptions import RestartBackup, StopOperation
from src.models import BackupConfig
from src.strategy import StrategyProtocol, get_strategy
from src.utils import Style


class Backup:
    @classmethod
    async def create(cls, config: BackupConfig, silent: bool = False):
        strategy = get_strategy(config.mode)
        cls = type("MixedBackup", (strategy, cls), {})
        self = await cls._create(config, silent)
        return self

    async def apply(self):
        assert isinstance(self, StrategyProtocol)
        while True:
            try:
                await self.make_backup()
                self.logger.success("备份完成")
                break
            except StopOperation as e:
                # 中止备份
                self.logger.warning(f"备份错误: {Style.RED(e)}")
            except RestartBackup as e:
                # 重启备份
                self.logger.warning(f"重启备份: {Style.RED(e)}")
                continue
            except Exception as e:
                self.logger.opt(exception=True).exception(f"未知错误: {Style.RED(e)}")
                self.logger.warning("重启备份...")
                continue
