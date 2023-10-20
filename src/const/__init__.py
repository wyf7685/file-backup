import pathlib as _p
import typing as _t

from . import _path

VERSION = "0.2.2"
PATH = _path

BackendType: _t.TypeAlias = _t.Literal["local", "server", "baidu"]
BackupMode: _t.TypeAlias = _t.Literal[
    "increment",
    "compress",
]
BackupUpdateType: _t.TypeAlias = _t.Literal["file", "dir", "del"]
StrPath: _t.TypeAlias = _t.Union[str, _p.Path]

BackupModeSet: _t.Set[str] = set(BackupMode.__args__)  # type: ignore


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
