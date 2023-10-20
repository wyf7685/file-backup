import os as _os
from pathlib import Path
from uuid import uuid4 as _uuid

DATA = Path("data")
CONFIG = DATA / "config.json"
CACHE = DATA / "cache"
_CACHE_NAME = "file-backup_" + str(_uuid()).split("-")[0]
CACHE = Path(_os.getenv("TEMP", CACHE)) / _CACHE_NAME

[p.mkdir(parents=True, exist_ok=True) for p in {DATA, CACHE}]
