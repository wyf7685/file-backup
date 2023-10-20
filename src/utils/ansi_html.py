import re
from typing import Any, Dict, TextIO, Tuple
from colorama.ansi import AnsiFore, AnsiBack, AnsiStyle
from colorama.ansitowin32 import AnsiToWin32

# Control Sequence Introducer
ANSI_CSI_RE = re.compile("\001?\033\\[((?:\\d|;)*)([a-zA-Z])\002?")

# Operating System Command
ANSI_OSC_RE = re.compile("\001?\033\\]([^\a]*)(\a)\002?")


class AnsiToHtml(AnsiToWin32):
    win32_calls: Dict[str, Tuple[Any, ...]]
    span_depth: int = 0

    def __init__(self, wrapped: TextIO) -> None:
        super().__init__(wrapped, True, False, False)
        self.win32_calls = {
            AnsiStyle.RESET_ALL: (self.reset_all,),
            AnsiStyle.BRIGHT: (self.disable,),
            AnsiStyle.DIM: (self.disable,),
            AnsiStyle.NORMAL: (self.disable,),
            AnsiFore.BLACK: (self.fore, "black"),
            AnsiFore.RED: (self.fore, "red"),
            AnsiFore.GREEN: (self.fore, "green"),
            AnsiFore.YELLOW: (self.fore, "#F5C500"),
            AnsiFore.BLUE: (self.fore, "blue"),
            AnsiFore.MAGENTA: (self.fore, "magenta"),
            AnsiFore.CYAN: (self.fore, "#5EB5FA"),
            AnsiFore.WHITE: (self.fore, "gray"),
            AnsiFore.RESET: (self.fore,),
            AnsiFore.LIGHTBLACK_EX: (self.fore, "#888483"),
            AnsiFore.LIGHTRED_EX: (self.fore, "#F94C48"),
            AnsiFore.LIGHTGREEN_EX: (self.fore, "#23D487"),
            AnsiFore.LIGHTYELLOW_EX: (self.fore, "#FAF740"),
            AnsiFore.LIGHTBLUE_EX: (self.fore, "#3C90ED"),
            AnsiFore.LIGHTMAGENTA_EX: (self.fore, "#DB6FD1"),
            AnsiFore.LIGHTCYAN_EX: (self.fore, "#2AB9D6"),
            AnsiFore.LIGHTWHITE_EX: (self.fore, "#ECE9E1"),
            AnsiBack.BLACK: (self.disable,),
            AnsiBack.RED: (self.disable,),
            AnsiBack.GREEN: (self.disable,),
            AnsiBack.YELLOW: (self.disable,),
            AnsiBack.BLUE: (self.disable,),
            AnsiBack.MAGENTA: (self.disable,),
            AnsiBack.CYAN: (self.disable,),
            AnsiBack.WHITE: (self.disable,),
            AnsiBack.RESET: (self.disable,),
            AnsiBack.LIGHTBLACK_EX: (self.disable,),
            AnsiBack.LIGHTRED_EX: (self.disable,),
            AnsiBack.LIGHTGREEN_EX: (self.disable,),
            AnsiBack.LIGHTYELLOW_EX: (self.disable,),
            AnsiBack.LIGHTBLUE_EX: (self.disable,),
            AnsiBack.LIGHTMAGENTA_EX: (self.disable,),
            AnsiBack.LIGHTCYAN_EX: (self.disable,),
            AnsiBack.LIGHTWHITE_EX: (self.disable,),
        }

    def fore(self, fore, *args, **kwargs) -> str:
        self.span_depth += 1
        return f'<span style="color:{fore}">'

    def reset_all(self, *args, **kwargs) -> str:
        tag = "</span>" * self.span_depth
        self.span_depth = 0
        return tag

    def disable(self, *args, **kwargs) -> str:
        self.span_depth += 1
        return "<span>"

    def call_win32(self, command, params) -> Any:
        if command == "m":
            for param in params:
                if param in self.win32_calls:
                    func_args = self.win32_calls[param]
                    func = func_args[0]
                    args = func_args[1:]
                    kwargs = dict(on_stderr=self.on_stderr)
                    return func(*args, **kwargs)

    def convert_ansi(self, paramstring, command) -> Any:
        params = self.extract_params(command, paramstring)
        return self.call_win32(command, params)

    def convert_osc(self, text) -> str:
        return text

    def write_and_convert(self, text) -> int:
        cursor = 0
        count = 0
        text = self.convert_osc(text)
        for match in self.ANSI_CSI_RE.finditer(text):
            start, end = match.span()
            self.write_plain_text(text, cursor, start)
            count += start - cursor
            span = self.convert_ansi(*match.groups()) or ""
            self.write_plain_text(span, 0, len(span))
            cursor = end
        self.write_plain_text(text, cursor, len(text))
        count += len(text) - cursor
        return count

    def write(self, text) -> int:
        return self.write_and_convert(text)


def _init_log_html() -> int:
    from datetime import date
    from io import StringIO
    from src.log import logger, default_filter, default_format

    def sink(msg: str) -> None:
        from src.models import config
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
