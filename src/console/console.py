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
    TypeAlias,
    final,
)

from src.const.exceptions import CommandExit, StopOperation
from src.log import get_logger
from src.utils import Style

from .input_queue import InputQueue

if TYPE_CHECKING:
    from src.log import Logger

T_Callback: TypeAlias = Callable[[List[str]], Awaitable[Any]]
T_Command: TypeAlias = Callable[[List[str]], Awaitable[Any]]
ConsoleExitKey: Set[str] = {"stop", "exit", "quit"}


@final
class Console(object):
    logger: "Logger" = get_logger("Console").opt(colors=True)
    _callback: Dict[str, List[T_Callback]] = defaultdict(list)
    _cmd_help: Dict[str, List[str]] = defaultdict(list)
    _queue: InputQueue = InputQueue()

    @classmethod
    async def start(cls) -> None:
        await cls._run()

    @classmethod
    async def _run(cls) -> None:
        cls.logger.info("开始监听控制台命令...")
        cls._queue.start()

        while True:
            cmd = await cls._queue.get()
            if cmd is None:
                cmd = "stop"

            args = cls.parse_cmd(cmd)
            key = args.pop(0) if args else ""

            if key in ConsoleExitKey:
                key = "stop"

            if key in cls._callback:
                await cls._run_command(key, args)
            elif key not in ConsoleExitKey:
                cls.logger.warning(f"未知命令: {cls.styled_command(key, *args)}")

            if key in ConsoleExitKey:
                cls.logger.info("正在退出...")
                return

    @classmethod
    def register(
        cls,
        key: str,
        help: Optional[str] = None,
        *,
        alias: List[str] = [],
    ):
        def decorator(func: T_Callback):
            for k in [key] + alias:
                cls._callback[k].append(func)

            if help is not None:
                cls._cmd_help[key].append(help)

            return func

        return decorator

    @classmethod
    async def _run_command(cls, key: str, args: List[str]) -> None:
        async def call(func: T_Callback):
            try:
                await func(args)
            except CommandExit as e:
                cls.logger.error(f"执行命令 {cls.styled_command(key, *args)} 时发生错误")
                cls.logger.error(e)
            except StopOperation as e:
                cls.logger.error(e)
            except Exception as e:
                cls.logger.error(f"命令 {cls.styled_command(key, *args)} 异常退出: {e}")

        await asyncio.gather(*[call(func) for func in cls._callback[key]])

    @staticmethod
    def parse_cmd(cmd: str) -> List[str]:
        cmd += " "
        args = []
        p = i = 0
        quote = False

        while i < len(cmd):
            if cmd[i] == '"':
                if quote:
                    args.append(cmd[p:i])
                    quote = False
                    p = i + 2
                    i += 1
                else:
                    quote = True
                    p = i + 1
            elif cmd[i] == " " and not quote:
                args.append(cmd[p:i])
                p = i + 1
            i += 1

        return [i for i in args if i]

    @staticmethod
    def check_arg_length(args: List[str], length: int, *lengths: int) -> List[str]:
        arr = [length, *lengths]
        if len(args) not in arr:
            raise CommandExit(f"应输入 {', '.join(str(i) for i in arr)} 个参数")
        return args

    @staticmethod
    def styled_arg(arg: str) -> str:
        return Style.BLUE(arg)

    @staticmethod
    def styled_command(cmd: str, *args: str) -> str:
        res = [Style.GREEN(cmd)]
        res.extend(Console.styled_arg(arg) for arg in args)
        return " ".join(res)
