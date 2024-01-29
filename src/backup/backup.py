import asyncio

from src.config import BackupConfig
from src.const.exceptions import RestartBackup, StopOperation
from src.strategy import StrategyProtocol, get_strategy
from src.utils import Style


class Backup(object):
    @classmethod
    async def create(cls, config: BackupConfig, *, silent: bool = False) -> "Backup":
        strategy = get_strategy(config.mode)
        MixedBackup = type("MixedBackup", (cls, strategy), {})
        self = await MixedBackup.init(config)
        if not silent:
            self.logger.success(f"{Style.GREEN("Backup")} [{Style.CYAN(config.name)}] 初始化成功")
        return self

    async def apply(self, *, max_try: int = 3) -> None:
        assert isinstance(self, StrategyProtocol)
        with self.logger.catch():
            for i in range(max_try):
                try_text = f"剩余重试次数: {Style.YELLOW(max_try-i-1)}/{Style.GREEN(max_try)}"
                try:
                    await self.make_backup()
                    self.logger.success("备份完成")
                    break
                except StopOperation as e:
                    # 中止备份
                    self.logger.warning(f"备份错误: {Style.RED(e)}")
                    break
                except RestartBackup as e:
                    # 重启备份
                    self.logger.warning(f"重启备份: {Style.RED(e)}")
                    self.logger.warning(try_text)
                except Exception as e:
                    self.logger.exception(f"未知错误: {Style.RED(e)}")
                    self.logger.warning("重启备份...")
                    self.logger.warning(try_text)
                await asyncio.sleep(1)
            else:
                self.logger.error("备份失败: 达到最大重试次数")
                return
