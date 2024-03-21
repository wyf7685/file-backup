from pathlib import Path

from .api_rm_file import rm_file
from .api_list_dir import list_dir


def rm_dir(path: str):
    for typ, name in list_dir(path):
        p = Path(path) / name
        if typ == "d":
            rm_dir(p.as_posix())
        else:
            rm_file(p)
