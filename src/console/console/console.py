import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Set

from src.const.exceptions import CommandExit, StopOperation
from src.log import get_logger

from .input_queue import InputQueue
from .utils import parse_cmd, styled_command

if TYPE_CHECKING:
    from src.log import Logger

type CommandCallback = Callable[[List[str]], Awaitable[Any]]
ConsoleExitKey: Set[str] = {"stop", "exit", "quit"}

__queue: InputQueue = InputQueue()
__callback: Dict[str, List[CommandCallback]] = defaultdict(list)
__cmd_help: Dict[str, List[str]] = defaultdict(list)
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

        if key in __callback:
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
    async def call(func: CommandCallback):
        try:
            await func(args)
        except CommandExit as e:
            logger.error(f"执行命令 {styled_command(key, *args)} 时发生错误")
            logger.error(e)
        except StopOperation as e:
            logger.error(e)
        except Exception as e:
            logger.exception(f"命令 {styled_command(key, *args)} 异常退出: {e}")

    await asyncio.gather(*[call(func) for func in __callback[key]])


def register(
    key: str,
    help: Optional[str] = None,
    *,
    alias: Optional[List[str]] = None,
):
    alias = alias or []

    def decorator(func: CommandCallback):
        for k in [key, *alias]:
            __callback[k].append(func)

        if help is not None:
            __cmd_help[key].append(help)

        return func

    return decorator


def get_cmd_help() -> Dict[str, List[str]]:
    return __cmd_help
