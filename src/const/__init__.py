import pathlib as _p
import typing as t

from . import path as _path

VERSION = "0.3.0"
PATH = _path

type BackendType = t.Literal["local", "server", "baidu"]
type BackupMode = t.Literal["increment", "compress"]
type BackupUpdateType = t.Literal["file", "dir", "del"]
type StrPath = t.Union[str, _p.Path]

BackupModeSet: t.Set[str] = {"increment", "compress"}


def __init() -> None:
    import atexit
    import shutil
    from contextlib import suppress

    from src.utils import clean_pycache

    def cleanup() -> None:
        clean_pycache()
        with suppress(Exception):
            shutil.rmtree(PATH.CACHE)

    atexit.register(cleanup)


__init()
