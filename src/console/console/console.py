from __future__ import annotations

import asyncio
import sys
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

import loguru

from src.const.exceptions import CommandExit, StopOperation
from src.log import get_logger
from src.utils import Style

from .utils import InputQueue, check_arg_length, parse_cmd, styled_command

type CommandCallback[**P, T] = Callable[P, Awaitable[T]]
ConsoleExitKey: Set[str] = {"stop", "exit", "quit"}


@dataclass
class CommandWrapper[**P, T]():
    name: str
    logger: loguru.Logger
    callback: CommandCallback[P, T]
    help: Optional[str]
    arglen: List[int]

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return await self.callback(*args, **kwargs)


__queue: InputQueue = InputQueue()
__cmd_wrapper: Dict[str, List[CommandWrapper[[List[str]], None]]] = defaultdict(list)
logger: loguru.Logger = get_logger("Console").opt(colors=True)


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

        if key in __cmd_wrapper:
            await __run_command(key, args)
        elif key not in ConsoleExitKey:
            logger.warning(f"未知命令: {styled_command(key, *args)}")

        if key in ConsoleExitKey:
            logger.info("正在退出...")
            return


async def start():
    # 搜索并加载控制台命令
    for module in [i for i in sys.modules if i.startswith("src.")]:
        name = module.split(".")[-1]
        with suppress(ImportError):
            import_module(f"{module}.{name}_cmd")
            logger.debug(f"加载模块命令: {Style.GREEN(name)}")

    await __run()


async def __run_command(key: str, args: List[str]) -> None:
    @logger.catch
    async def call(wrapper: CommandWrapper[[List[str]], Any]):
        try:
            if wrapper.arglen:
                check_arg_length(args, *wrapper.arglen)
            await wrapper(args)
        except CommandExit as e:
            logger.error(f"执行命令 {styled_command(key, *args)} 时发生错误")
            logger.opt(exception=e.trace, colors=True).error(Style.RED(e, False))
        except StopOperation as e:
            logger.error(Style.RED(e, False))
        except Exception as e:
            logger.exception(f"命令 {styled_command(key, *args)} 异常退出: {e}")

    await asyncio.gather(*[call(info) for info in __cmd_wrapper[key]])


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

    def decorator(func: CommandCallback[[List[str]], None]):
        wrapper = CommandWrapper(
            name=key,
            logger=logger.bind(head=key),
            callback=func,
            help=help,
            arglen=arglen,
        )

        for k in [key, *alias]:
            __cmd_wrapper[k].append(wrapper)

        return wrapper

    return decorator


def get_cmd_help() -> Dict[str, List[str]]:
    return {
        key: [v.help for v in value if v.help and v.name == key]
        for key, value in __cmd_wrapper.items()
    }
