import typing as _t
import functools


class _StyleInt(int):
    @functools.cache
    def __keys(self) -> _t.List[str]:
        keys = []  # type: _t.List[str]
        k = 1
        style = self
        while style:
            if style & 1:
                keys.append(_STYLE_MAP[_StyleInt(k)])
            style >>= 1
            k <<= 1
        return keys

    @functools.cache
    def __call__(self, value: _t.Any, fix: bool = True) -> str:
        text = str(value)
        if fix:
            text = text.replace("<", "\\<")
        for key in self.__keys():
            text = f"<{key}>{text}</{key}>"
        return text

    def __or__(self, value: int) -> _t.Self:
        return type(self)(int(self) | int(value))

    def __repr__(self) -> str:
        return f"<StyleInt {super().__repr__()}: {','.join(self.__keys())}>"

    def __str__(self) -> str:
        return self.__repr__()


def StyleInt(*args: int) -> _StyleInt:
    num = 0
    for i in args:
        num |= 1 << i
    return _StyleInt(num)


class Style:
    # Fore
    BLACK = StyleInt(0)
    RED = StyleInt(1)
    GREEN = StyleInt(2)
    YELLOW = StyleInt(3)
    BLUE = StyleInt(4)
    MAGENTA = StyleInt(5)
    CYAN = StyleInt(6)
    WHITE = StyleInt(7)
    LIGHTBLACK_EX = StyleInt(8)
    LIGHTRED_EX = StyleInt(9)
    LIGHTGREEN_EX = StyleInt(10)
    LIGHTYELLOW_EX = StyleInt(11)
    LIGHTBLUE_EX = StyleInt(12)
    LIGHTMAGENTA_EX = StyleInt(13)
    LIGHTCYAN_EX = StyleInt(14)
    LIGHTWHITE_EX = StyleInt(15)
    # Style
    BOLD = StyleInt(16)
    DIM = StyleInt(17)
    NORMAL = StyleInt(18)
    HIDE = StyleInt(19)
    ITALIC = StyleInt(20)
    BLINK = StyleInt(21)
    STRIKE = StyleInt(22)
    UNDERLINE = StyleInt(23)
    REVERSE = StyleInt(24)
    # Mix
    PATH = StyleInt(3, 23)
    PATH_DEBUG = StyleInt(12, 20, 23)


_STYLE_MAP: _t.Dict[_StyleInt, str] = {
    Style.BLACK: "k",
    Style.RED: "r",
    Style.GREEN: "g",
    Style.YELLOW: "y",
    Style.BLUE: "e",
    Style.MAGENTA: "m",
    Style.CYAN: "c",
    Style.WHITE: "w",
    Style.LIGHTBLACK_EX: "lk",
    Style.LIGHTRED_EX: "lr",
    Style.LIGHTGREEN_EX: "lg",
    Style.LIGHTYELLOW_EX: "ly",
    Style.LIGHTBLUE_EX: "le",
    Style.LIGHTMAGENTA_EX: "lm",
    Style.LIGHTCYAN_EX: "lc",
    Style.LIGHTWHITE_EX: "lw",
    Style.UNDERLINE: "u",
    Style.BOLD: "b",
    Style.DIM: "d",
    Style.NORMAL: "n",
    Style.HIDE: "h",
    Style.ITALIC: "i",
    Style.BLINK: "l",
    Style.STRIKE: "s",
    Style.UNDERLINE: "u",
    Style.REVERSE: "v",
}
