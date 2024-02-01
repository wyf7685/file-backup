import asyncio
import time
from threading import Thread
from typing import List, Optional
from queue import Queue

from src.const.exceptions import CommandExit
from src.utils import Style


class InputQueue(object):
    _queue: Queue[str]
    _running: bool
    _thread: Thread

    def _run(self) -> None:
        while self._running:
            try:
                self._queue.put(input())
            except EOFError:
                self._running = False
            time.sleep(0.05)

    def start(self) -> None:
        self._queue = Queue(0)
        self._running = True
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    async def get(self) -> Optional[str]:
        while self._running:
            if not self._queue.empty():
                return self._queue.get()
            await asyncio.sleep(0.05)


def parse_cmd(cmd: str) -> List[str]:
    cmd += " "
    args: List[str] = []
    p = i = 0
    quote = None

    while i < len(cmd):
        if cmd[i] in {'"', "'"}:
            if quote == cmd[i]:
                args.append(cmd[p:i])
                quote = None
                p = i + 2
                i += 1
            elif quote is None:
                quote = cmd[i]
                p = i + 1
        elif cmd[i] == " " and quote is None:
            args.append(cmd[p:i])
            p = i + 1
        i += 1

    return [i for i in args if i]


def check_arg_length(args: List[str], length: int, *lengths: int) -> List[str]:
    arr = [length, *lengths]
    if len(args) not in arr:
        expect = Style.YELLOW("/".join(str(i) for i in arr))
        got = Style.YELLOW(len(args))
        raise CommandExit(f"应输入 {expect} 个参数, 得到了 {got} 个")
    return args


def styled_arg(arg: str) -> str:
    return Style.BLUE(arg)


def styled_command(cmd: str, *args: str) -> str:
    return " ".join(
        [
            Style.GREEN(cmd),
            *(styled_arg(f'"{arg}"' if " " in arg else arg) for arg in args),
        ]
    )
