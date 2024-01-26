import functools
import json
import pathlib
import typing
from json import load, loads


class _PathEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any):
        return obj.as_posix() if isinstance(obj, pathlib.Path) else super().default(obj)


dump = functools.partial(json.dump, cls=_PathEncoder)
dumps = functools.partial(json.dumps, cls=_PathEncoder)
