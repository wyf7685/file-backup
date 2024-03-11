from __future__ import annotations

import logging
import sys
import typing as _t

import loguru


logger: loguru.Logger = loguru.logger.opt()

DEFAULT_LOG_LEVEL: str = "DEBUG"


class LoguruHandler(logging.Handler):
    """logging 与 loguru 之间的桥梁，将 logging 的日志转发到 loguru。"""

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6  # type: ignore
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class Filter:
    level: int | str = DEFAULT_LOG_LEVEL

    def update_level(self, level: int | str | None = None) -> int:
        if level is None:
            level = self.level
        self.level = logger.level(level).no if isinstance(level, str) else level
        return self.level

    def __call__(self, record: loguru.Record) -> bool:
        if not isinstance(self.level, int):
            try:
                self.level = self.update_level()
            except Exception:
                print(
                    "===============================================================",
                    f"WARNING: log level must be an integer or a string, not {repr(self.level)}",
                    f"Automatically reset to {DEFAULT_LOG_LEVEL}",
                    "===============================================================",
                    sep="\n",
                    end="\n",
                )
                self.level = logger.level(DEFAULT_LOG_LEVEL).no

        return record["level"].no >= self.level


class Format:
    __DEBUG_LEVEL_NO: int = logger.level("DEBUG").no
    fmt = [
        "<g>{time:MM-DD HH:mm:ss}</g> [<lvl>{level}</lvl>]",
        "<c><u>{name}</u></c> |",
        "<c>{file}</c>:<c>{line}</c> |",
        "{message}\n{exception}",
    ]

    def __call__(self, record: loguru.Record) -> str:
        fmt = self.fmt.copy()

        if name := record["extra"].get("name"):
            fmt[1] = fmt[1].format(name=name)

        if head := record["extra"].get("head"):
            fmt.insert(3, f"<m>{head}</m> |")

        if record["level"].no > self.__DEBUG_LEVEL_NO:
            # Not debug, remove file/line information
            fmt.pop(2)

        return " ".join(fmt)


LOGGING_CONFIG: _t.Dict[str, _t.Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": f"{__name__}.LoguruHandler",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": [], "level": "INFO"},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO"},
    },
}

default_filter = Filter()
"""默认日志等级过滤器"""
default_format = Format()
"""默认日志格式"""


def init_logger_sink() -> tuple[int, int]:
    logger.remove()
    return logger.add(
        sys.stdout,
        level=0,
        diagnose=False,
        filter=default_filter,
        format=default_format,
        enqueue=True,
        colorize=True,
    ), logger.add(
        "./logs/{time:YYYY-MM-DD}.log",
        rotation="00:00",
        level=0,
        diagnose=True,
        filter=default_filter,
        format=default_format,
        enqueue=True,
        colorize=False,
    )


def get_logger(
    name: str | None = None,
    head: str | None = None,
) -> loguru.Logger:
    return logger.bind(name=name, head=head)


def set_log_level(level: int | str) -> int:
    return default_filter.update_level(level)


getLogger = get_logger
setLogLevel = set_log_level
stdout_id, file_id = init_logger_sink()
