from typing import List

from src.console import Console
from src.utils import Style
from src.const.exceptions import CommandExit
from src.models import find_backup

from .recover import Recover


@Console.register("recover", "恢复到备份")
async def cmd_recover(args: List[str]) -> None:
    if not args:
        command = Console.styled_command("recover", "<name>", "<uuid>")
        Console.logger.info(f"{command} - 恢复到备份项的备份记录")
        return

    Console.check_arg_length(args, 2)

    name, uuid = args

    backup = find_backup(name)
    if backup is None:
        raise CommandExit(f"未找到名为 [{Style.CYAN(name)}] 的备份项")

    recover = Recover(backup)
    await recover.load_record_list()
    record = recover.get_record(uuid)
    if record is None:
        raise CommandExit(f"未找到 uuid 为 [{Style.CYAN(uuid)}] 的备份")
    
    await recover.apply(record)
