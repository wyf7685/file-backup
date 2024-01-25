from typing import List

from src.const.exceptions import CommandExit
from src.utils import Style


def parse_cmd(cmd: str) -> List[str]:
    cmd += " "
    args = []
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
        raise CommandExit(f"应输入 {'/'.join(str(i) for i in arr)} 个参数")
    return args


def styled_arg(arg: str) -> str:
    return Style.BLUE(arg)


def styled_command(cmd: str, *args: str) -> str:
    # res = [Style.GREEN(cmd)]
    # for arg in args:
    #     if " " in arg:
    #         arg = f'"{arg}"'
    #     res.append(styled_arg(arg))
    # return " ".join(res)

    return " ".join([
        Style.GREEN(cmd),
        *(styled_arg(f'"{arg}"' if " " in arg else arg) for arg in args),
    ])
