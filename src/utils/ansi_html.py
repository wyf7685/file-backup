import functools
import re
from functools import partial
from typing import Callable, Dict, Sequence, TextIO, override

from colorama.ansi import AnsiBack, AnsiFore, AnsiStyle
from colorama.ansitowin32 import AnsiToWin32

# Control Sequence Introducer
ANSI_CSI_RE = re.compile("\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?")

# Operating System Command
ANSI_OSC_RE = re.compile("\001?\033\\]([^\a]*)(\a)\002?")


class AnsiToHtml(AnsiToWin32):
    win32_calls: Dict[str, Callable[[], str]]
    span_depth: int = 0

    @override
    def __init__(self, wrapped: TextIO) -> None:
        super().__init__(wrapped, True, False, False)
        self.win32_calls = {
            AnsiStyle.RESET_ALL: self.reset_all,
            AnsiStyle.BRIGHT: self.disable,
            AnsiStyle.DIM: self.disable,
            AnsiStyle.NORMAL: self.disable,
            AnsiFore.BLACK: partial(self.fore, "black"),
            AnsiFore.RED: partial(self.fore, "red"),
            AnsiFore.GREEN: partial(self.fore, "green"),
            AnsiFore.YELLOW: partial(self.fore, "#F5C500"),
            AnsiFore.BLUE: partial(self.fore, "blue"),
            AnsiFore.MAGENTA: partial(self.fore, "magenta"),
            AnsiFore.CYAN: partial(self.fore, "#5EB5FA"),
            AnsiFore.WHITE: partial(self.fore, "gray"),
            AnsiFore.RESET: self.reset_all,
            AnsiFore.LIGHTBLACK_EX: partial(self.fore, "#888483"),
            AnsiFore.LIGHTRED_EX: partial(self.fore, "#F94C48"),
            AnsiFore.LIGHTGREEN_EX: partial(self.fore, "#23D487"),
            AnsiFore.LIGHTYELLOW_EX: partial(self.fore, "#FAF740"),
            AnsiFore.LIGHTBLUE_EX: partial(self.fore, "#3C90ED"),
            AnsiFore.LIGHTMAGENTA_EX: partial(self.fore, "#DB6FD1"),
            AnsiFore.LIGHTCYAN_EX: partial(self.fore, "#2AB9D6"),
            AnsiFore.LIGHTWHITE_EX: partial(self.fore, "#ECE9E1"),
            AnsiBack.BLACK: self.disable,
            AnsiBack.RED: self.disable,
            AnsiBack.GREEN: self.disable,
            AnsiBack.YELLOW: self.disable,
            AnsiBack.BLUE: self.disable,
            AnsiBack.MAGENTA: self.disable,
            AnsiBack.CYAN: self.disable,
            AnsiBack.WHITE: self.disable,
            AnsiBack.RESET: self.reset_all,
            AnsiBack.LIGHTBLACK_EX: self.disable,
            AnsiBack.LIGHTRED_EX: self.disable,
            AnsiBack.LIGHTGREEN_EX: self.disable,
            AnsiBack.LIGHTYELLOW_EX: self.disable,
            AnsiBack.LIGHTBLUE_EX: self.disable,
            AnsiBack.LIGHTMAGENTA_EX: self.disable,
            AnsiBack.LIGHTCYAN_EX: self.disable,
            AnsiBack.LIGHTWHITE_EX: self.disable,
        }

    def fore(self, fore) -> str:
        self.span_depth += 1
        return f'<span style="color:{fore}">'

    def reset_all(self) -> str:
        tag = "</span>" * self.span_depth
        self.span_depth = 0
        return tag

    def disable(self) -> str:
        self.span_depth += 1
        return "<span>"

    @functools.cache
    @override
    def call_win32(self, command: str, params: Sequence[int]) -> str:
        if command == "m":
            for param in params:
                if param in self.win32_calls:
                    return self.win32_calls[param]()
        return ""

    @override
    def convert_ansi(self, paramstring: str, command: str) -> str:
        params = self.extract_params(command, paramstring)
        return self.call_win32(command, params)

    @override
    def convert_osc(self, text: str) -> str:
        return text

    @override
    def write_and_convert(self, text: str) -> int:
        cursor = 0
        count = 0
        text = self.convert_osc(text)
        for m in self.ANSI_CSI_RE.finditer(text):
            start, end = m.span()
            self.write_plain_text(text, cursor, start)
            count += start - cursor
            span = self.convert_ansi(*m.groups())
            self.write_plain_text(span, 0, len(span))
            cursor = end
        self.write_plain_text(text, cursor, len(text))
        count += len(text) - cursor
        return count

    @override
    def write(self, text: str) -> int:
        return self.write_and_convert(text)


def _init_log_html() -> int:
    from datetime import date
    from io import StringIO

    from src.log import default_filter, default_format, logger

    def sink(msg: str) -> None:
        from src.config import config
        if not config.experiment.log_html:
            return

        file = f'logs/{date.today().strftime("%Y-%m-%d")}.html'
        stream = StringIO()
        AnsiToHtml(stream).write(msg)
        text = stream.getvalue().strip("\n")
        with open(file, "a", encoding="utf-8") as f:
            f.write(f"{text}<br/>\n")
        stream.close()

    return logger.add(
        sink,
        level=0,
        diagnose=False,
        filter=default_filter,
        format=default_format,
        enqueue=True,
        colorize=True,
    )


html_log_id = _init_log_html()
