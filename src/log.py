import sys
import loguru
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from loguru import Logger, Record


logger: "Logger" = loguru.logger.opt()

DEFAULT_LOG_LEVEL: str = "DEBUG"


class Filter:
    level: Union[int, str] = DEFAULT_LOG_LEVEL

    def update_level(self, level: Optional[Union[int, str]] = None) -> None:
        if level is None:
            level = self.level
        self.level = logger.level(level).no if isinstance(level, str) else level

    def __call__(self, record: "Record") -> bool:
        if log_name := record["extra"].get("name"):
            record["name"] = log_name

        if not isinstance(self.level, int):
            try:
                self.update_level()
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
        
        return record["level"].no >= self.level # type: ignore


class Format:
    _debug_level_no: int = logger.level("DEBUG").no

    fmt: str = (
        "<g>{time:MM-DD HH:mm:ss}</g> "
        "[<lvl>{level}</lvl>] "
        "<c><u>{name}</u></c> | "
        "{message}\n"
    )
    fmt_debug: str = (
        "<g>{time:MM-DD HH:mm:ss}</g> "
        "[<lvl>{level}</lvl>] "
        "<c><u>{name}</u></c> | "
        "<c>{file}</c>:<c>{line}</c> | "
        "{message}\n"
    )

    def __call__(self, record: "Record") -> str:
        return (
            self.fmt_debug
            if record["level"].no <= self._debug_level_no
            else self.fmt
        )


default_filter: Filter = Filter()
"""默认日志等级过滤器"""
default_format: Format = Format()
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
        diagnose=False,
        filter=default_filter,
        format=default_format,
        enqueue=True,
        colorize=False,
    )


def get_logger(name: Optional[str] = None) -> "Logger":
    return logger.bind(name=name) if name else logger


def set_log_level(level: Union[int, str]) -> None:
    default_filter.update_level(level)


getLogger = get_logger
setLogLevel = set_log_level
stdout_id, file_id = init_logger_sink()
