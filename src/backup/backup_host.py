import asyncio
from datetime import datetime
from typing import Dict, TYPE_CHECKING

from src.log import get_logger
from src.models import BackupConfig, Style, config
from src.utils import Style

from .backup import Backup

if TYPE_CHECKING:
    from src.log import Logger

class BackupHost(object):
    logger: "Logger" = get_logger("BackupHost").opt(colors=True)
    _last_run: Dict[str, float] = {}
    _running: bool = False
    _task: asyncio.Task[None]
    _backup_task: Dict[str, asyncio.Task[None]] = {}

    @classmethod
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
    async def stop(cls):
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
    async def run_backup(cls, backup: BackupConfig) -> None:
        cls.logger.info(f"创建备份任务: [{Style.CYAN(backup.name)}]")
        cls._last_run[backup.name] = datetime.now().timestamp()
        task = asyncio.create_task(Backup(backup).apply())
        cls._backup_task[backup.name] = task
