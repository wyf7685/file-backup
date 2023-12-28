import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Dict

from src.log import get_logger
from src.models import BackupConfig, Style, config
from src.utils import Style

from .backup import Backup

if TYPE_CHECKING:
    from src.log import Logger


class BackupHost(object):
    logger: ClassVar["Logger"] = get_logger("BackupHost").opt(colors=True)
    _last_run: ClassVar[Dict[str, float]] = {}
    _running: ClassVar[bool] = False
    _task: ClassVar[asyncio.Task[None]]
    _backup_task: ClassVar[Dict[str, asyncio.Task[None]]] = {}

    @classmethod
    @logger.catch
    async def _run(cls) -> None:
        while cls._running:
            # 判断备份任务是否已完成
            for name in list(cls._backup_task):
                if cls._backup_task[name].done():
                    del cls._backup_task[name]

            # 遍历备份任务清单, 执行备份
            for backup in config.backup_list:
                if backup.name in cls._backup_task:
                    continue
                now = datetime.now().timestamp()
                last_run = cls._last_run.get(backup.name)
                if last_run is None or last_run - now > backup.interval:
                    await cls.run_backup(backup)
            await asyncio.sleep(1)

    @classmethod
    async def start(cls) -> None:
        cls.logger.info(f"正在初始化 {Style.GREEN('BackupHost')} ...")
        cls.logger.info("开始备份...")
        cls._running = True
        cls._task = asyncio.create_task(cls._run())

    @classmethod
    async def stop(cls) -> None:
        if not cls._running:
            return

        cls._running = False
        cls.logger.info("等待备份进程退出...")
        while not cls._task.done():
            await asyncio.sleep(0.05)

        for task in cls._backup_task.values():
            while not task.done():
                await asyncio.sleep(0.05)
        cls.logger.info(f"{Style.GREEN('BackupHost')} 已终止")

    @classmethod
    @logger.catch
    async def run_backup(cls, config: BackupConfig) -> None:
        cls.logger.info(f"创建备份任务: [{Style.CYAN(config.name)}]")
        cls._last_run[config.name] = datetime.now().timestamp()
        backup = await Backup.create(config)
        task = asyncio.create_task(backup.apply())
        cls._backup_task[config.name] = task
