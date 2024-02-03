import pathlib as _p
import typing as _t

from . import path as _path

VERSION = "0.4.0"
PATH = _path

type BackendType = _t.Literal["local", "server", "baidu"]
type BackupMode = _t.Literal["increment", "compress"]
type BackupUpdateType = _t.Literal["file", "dir", "del"]
type StrPath = _t.Union[str, _p.Path]

BackupModeSet: _t.Set[str] = {"increment", "compress"}


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
