import asyncio
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    TypedDict,
)

from src.const.exceptions import CommandExit, StopOperation
from src.log import get_logger
from src.utils import Style

from .utils import parse_cmd, styled_command, InputQueue, check_arg_length

if TYPE_CHECKING:
    from src.log import Logger

type CommandCallback = Callable[[List[str]], Awaitable[Any]]
ConsoleExitKey: Set[str] = {"stop", "exit", "quit"}


class CommandInfo(TypedDict):
    name: str
    callback: CommandCallback
    help: Optional[str]
    arglen: List[int]


__queue: InputQueue = InputQueue()
__cmd_info: Dict[str, List[CommandInfo]] = defaultdict(list)
logger: "Logger" = get_logger("Console").opt(colors=True)


async def __run():
    logger.info("开始监听控制台命令...")
    __queue.start()

    while True:
        cmd = await __queue.get()
        if cmd is None:
            cmd = "stop"

        args = parse_cmd(cmd)
        key = args.pop(0) if args else ""

        if key in ConsoleExitKey:
            key = "stop"

        if key in __cmd_info:
            await __run_command(key, args)
        elif key not in ConsoleExitKey:
            logger.warning(f"未知命令: {styled_command(key, *args)}")

        if key in ConsoleExitKey:
            logger.info("正在退出...")
            return


async def start():
    await __run()


async def __run_command(key: str, args: List[str]) -> None:
    @logger.catch
    async def call(info: CommandInfo):
        try:
            if info["arglen"]:
                check_arg_length(args, *info["arglen"])
            await info["callback"](args)
        except CommandExit as e:
            logger.error(f"执行命令 {styled_command(key, *args)} 时发生错误")
            logger.error(Style.RED(e, False))
        except StopOperation as e:
            logger.error(Style.RED(e, False))
        except Exception as e:
            logger.exception(f"命令 {styled_command(key, *args)} 异常退出: {e}")

    await asyncio.gather(*[call(info) for info in __cmd_info[key]])


def register(
    key: str,
    help: Optional[str] = None,
    *,
    alias: Optional[List[str]] = None,
    arglen: Optional[List[int] | int] = None,
):
    alias = alias or []
    if isinstance(arglen, int):
        arglen = [arglen]
    arglen = arglen or []

    def decorator(func: CommandCallback):
        info: CommandInfo = {
            "name": key,
            "callback": func,
            "help": help,
            "arglen": arglen,
        }

        for k in [key, *alias]:
            __cmd_info[k].append(info)

        return func

    return decorator


def get_cmd_help() -> Dict[str, List[str]]:
    return {
        key: [v["help"] for v in value if v["help"] and v["name"] == key]
        for key, value in __cmd_info.items()
    }
