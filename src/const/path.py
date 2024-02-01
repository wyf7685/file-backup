import os as _os
import pathlib as _p
from uuid import uuid4 as _uuid

DATA = _p.Path("data")
CONFIG = DATA / "config.json"
__CACHE_NAME = "file-backup_" + str(_uuid()).split("-")[0]
CACHE = _p.Path(_os.getenv("TEMP", DATA / "cache")) / __CACHE_NAME

[p.mkdir(parents=True, exist_ok=True) for p in {DATA, CACHE}]
