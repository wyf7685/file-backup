import os as _os
from pathlib import Path
from uuid import uuid4 as _uuid

DATA = Path("data")
CONFIG = DATA / "config.json"
CACHE = DATA / "cache"
__cache_name = "file-backup_" + str(_uuid()).split("-")[0]
CACHE = Path(_os.getenv("TEMP", CACHE)) / __cache_name

[p.mkdir(parents=True, exist_ok=True) for p in {DATA, CACHE}]
