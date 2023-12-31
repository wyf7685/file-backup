from typing import List

from src.console import Console
from src.utils import Style
from src.const.exceptions import CommandExit
from src.models import find_backup

from .backup_host import BackupHost


@Console.register("backup", "执行备份")
async def cmd_backup(args: List[str]) -> None:
    if not args:
        command = Console.styled_command("backup", "<name>")
        Console.logger.info(f"{command} - 执行备份")
        return

    Console.check_arg_length(args, 1)

    name = args.pop(0)
    backup = find_backup(name)

    if backup is None:
        raise CommandExit(f"未找到名为 [{Style.CYAN(name)}] 的备份项")

    await BackupHost.run_backup(backup)


@Console.register("stop", "退出程序")
async def cmd_stop_host(*_) -> None:
    await BackupHost.stop()


@Console.register("reload", alias=["r"])
async def cmd_reload_host(*_) -> None:
    await BackupHost.stop()
    # BackupHost.start()
    await BackupHost.start()