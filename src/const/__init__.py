import pathlib as _p
import typing as t

from . import path as _path


VERSION = "0.2.2"
PATH = _path

BackendType = t.Literal["local", "server", "baidu"]
BackupMode = t.Literal["increment", "compress"]
BackupUpdateType = t.Literal["file", "dir", "del"]
StrPath = t.Union[str, _p.Path]

BackupModeSet: t.Set[str] = set(BackupMode.__args__)  # type: ignore


def _init() -> None:
    import atexit
    import shutil
    from contextlib import suppress

    from src.utils import clean_pycache

    def cleanup() -> None:
        clean_pycache()
        with suppress(Exception):
            shutil.rmtree(PATH.CACHE)

    atexit.register(cleanup)


_init()
