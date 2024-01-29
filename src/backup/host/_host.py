import asyncio
from datetime import datetime
from typing import Dict

from src.config import BackupConfig, config
from src.log import get_logger
from src.utils import Style

from ..backup import Backup

__logger = get_logger("BackupHost").opt(colors=True)
__last_run: Dict[str, datetime] = {}
__running: bool = False
__task: asyncio.Task[None]
__backup_task: Dict[str, asyncio.Task[None]] = {}


@__logger.catch
async def run_backup(config: BackupConfig) -> None:
    __logger.info(f"创建备份任务: [{Style.CYAN(config.name)}]")
    __last_run[config.name] = datetime.now()
    backup = await Backup.create(config)
    task = asyncio.create_task(backup.apply())
    __backup_task[config.name] = task


@__logger.catch()
async def __run() -> None:
    while __running:
        # 判断备份任务是否已完成
        for name in list(__backup_task):
            if __backup_task[name].done():
                del __backup_task[name]

        # 遍历备份任务清单, 执行备份
        for backup in config.backup_list:
            if backup.name in __backup_task:
                continue
            now = datetime.now()
            last_run = __last_run.get(backup.name)
            if (
                last_run is None
                or (last_run - now).microseconds / 1000 > backup.interval
            ):
                await run_backup(backup)
        await asyncio.sleep(1)


async def start() -> None:
    global __running, __task
    __logger.info(f"正在初始化 {Style.GREEN('BackupHost')} ...")
    __logger.info("开始备份...")
    __running = True
    __task = asyncio.create_task(__run())


async def stop() -> None:
    global __running
    if not __running:
        return

    __running = False
    __logger.info("等待备份进程退出...")
    while not __task.done():
        await asyncio.sleep(0.05)

    for task in __backup_task.values():
        while not task.done():
            await asyncio.sleep(0.05)
    __logger.info(f"{Style.GREEN('BackupHost')} 已终止")
