import json
from pathlib import Path
from typing import List, cast

from src.backend import Backend, get_backend
from src.config import BackupConfig, config
from src.const import PATH, BackupMode, BackupModeSet
from src.const.exceptions import CommandExit
from src.log import set_log_level
from src.models import BackupRecord, find_backup
from src.utils import Style, get_uuid

from . import console as Console


async def backend() -> Backend:
    return await get_backend().create()


@Console.register("help", "显示此帮助列表", alias=["?", "h"], arglen=0)
async def cmd_help(_) -> None:
    logger = cmd_help.logger
    helps = Console.console.get_cmd_help()

    length = max(len(k) + len(v) for k, v in helps.items()) + 16

    logger.info((Style.YELLOW | Style.BOLD)("帮助列表".center(length - 4)))
    logger.info("=" * length)
    for cmd, helps in sorted(helps.items()):
        for help in helps:
            logger.info(f"{Style.GREEN(cmd)} - {help}")


# @Console.register("reload", "重载配置文件", alias=["r"])
# async def cmd_reload(*_) -> None:
#     try:
#         config.reload()
#         Console.logger.success("配置文件重载成功!")
#     except Exception as err:
#         Console.logger.error(f"配置文件重载失败: {err}")


def format_backup_info(backup: BackupConfig) -> List[str]:
    return [
        f"本地路径: {Style.PATH(backup.local_path)}",
        f"备份模式: {Style.GREEN(backup.mode)}",
        f"备份间隔: {Style.GREEN(f'{backup.interval}s')}",
    ]


@Console.register("list", "列出所有备份项", alias=["ls"], arglen=0)
async def cmd_list(_) -> None:
    logger = cmd_list.logger
    logger.info("备份项列表")
    logger.info("================================")
    for i, backup in enumerate(config.backup_list):
        logger.info(f"{i+1}. [{Style.CYAN(backup.name)}]")
        for info in format_backup_info(backup):
            logger.info(f"    {info}")


@Console.register("query", "查询备份记录", alias=["q"], arglen=[0, 1])
async def cmd_query(args: List[str]) -> None:
    logger = cmd_query.logger

    if not args:
        command = Console.styled_command("query", "<name>")
        logger.info(f"{command} - 查询 {Console.styled_arg('<name>')} 的备份记录")
        return

    [name] = args
    backup = find_backup(name)
    if backup is None:
        raise CommandExit(f"未找到名为 [{Style.CYAN(name)}] 的备份项")

    remote_fp = backup.get_remote() / "backup.json"
    cache_fp = PATH.CACHE / get_uuid()
    client = await backend()
    if not await client.get_file(cache_fp, remote_fp):
        raise CommandExit(f"[{Style.CYAN(name)}] 的备份记录下载失败")

    raw = json.loads(cache_fp.read_text())
    cache_fp.unlink(True)

    logger.info(f"[{Style.CYAN(name)}] 的备份记录")
    logger.info("================================")
    for i, obj in enumerate(raw):
        record = BackupRecord.model_validate(obj)
        logger.info(f"备份记录 - {Style.YELLOW(f'id = {i+1}')}")
        logger.info(f"    时间: {Style.GREEN(record.timestr)}")
        logger.info(f"    uuid: {Style.CYAN(record.uuid)}")


@Console.register("add", "添加备份项", arglen=[0, 4])
async def cmd_add(args: List[str]) -> None:
    logger = cmd_add.logger

    if not args:
        command = Console.styled_command(
            "add", "<name>", "<mode>", "<interval>", "<local>"
        )
        logger.info(f"{command} - 添加备份项")
        return

    name, mode, interval, local = args

    if find_backup(name) is not None:
        raise CommandExit(f"{Style.BLUE('备份项')} [{Style.CYAN(name)}] 已存在, 请勿重复创建!")

    if mode not in BackupModeSet:
        mode_str = ", ".join(Style.YELLOW(i) for i in BackupModeSet)
        raise CommandExit(
            f"{Style.BLUE('备份模式')} 必须是 {mode_str} 中的一个, 不能是 {Style.YELLOW(mode)}"
        )

    try:
        interval = int(interval)
    except ValueError as e:
        raise CommandExit(
            f"{Style.BLUE('备份间隔')} 必须是整型, 不能是 {Style.YELLOW(interval)}"
        ) from e

    local_path = Path(local).absolute()
    if not local_path.exists():
        raise CommandExit(f"{Style.BLUE('备份路径')} {Style.PATH(local)} 不存在")

    backup = BackupConfig(
        name=name,
        mode=cast(BackupMode, mode),
        local_path=local_path,
        interval=interval,
    )
    config.backup_list.append(backup)
    config.save()

    logger.success("备份项添加成功!")
    logger.info(f"备份项: [{Style.CYAN(backup.name)}]")
    for info in format_backup_info(backup):
        logger.info(f"    {info}")


@Console.register("remove", "移除备份项", arglen=[0, 1])
async def cmd_remove(args: List[str]) -> None:
    logger = cmd_remove.logger

    if not args:
        command = Console.styled_command("remove", "<name>")
        logger.info(f"{command} - 移除备份项")
        return

    [name] = args
    backup = find_backup(name)

    if backup is None:
        raise CommandExit(f"未找到名为 [{Style.CYAN(name)}] 的备份项")

    config.backup_list.remove(backup)
    config.save()

    logger.success(f"已移除备份项 [{Style.CYAN(name)}]")


@Console.register("log-level", "修改日志等级", arglen=[0, 1])
async def cmd_log_level(args: List[str]) -> None:
    logger = cmd_log_level.logger

    if not args:
        command = Console.styled_command("log-level", "<level>")
        logger.info(f"{command} - 临时修改日志等级为 {Console.styled_arg('<level>')}")
        return

    level = args.pop(0).upper()
    try:
        set_log_level(level)
    except Exception as e:
        err_msg = Style.RED(f"{e.__class__.__name__}: {e}")
        raise CommandExit(f"修改日志等级为 {Style.YELLOW(level)} 时出现错误: {err_msg}") from e

    logger.info(f"已将当前日志等级修改为: {Style.YELLOW(level)}")


# @Console.register("test", "测试命令")
# async def cmd_test(args: List[str]) -> None:
#     Console.logger.info(f"测试: {Console.styled_command("test", *args)}")

# ctx = {}
# @Console.register("exec", "执行Python语句")
# async def cmd_exec(args: List[str]) -> None:
#     cmd = []
#     for arg in args:
#         if " " in arg:
#             arg = f'"{arg}"'
#         cmd.append(arg)
#     source = ' '.join(cmd)
#     exec(source, ctx)
