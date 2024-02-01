import functools
import json
import pathlib
import typing
from json import load as load, loads as loads


class _PathEncoder(json.JSONEncoder):
    def default(self, o: typing.Any):
        return o.as_posix() if isinstance(o, pathlib.Path) else super().default(o)


dump = functools.partial(json.dump, cls=_PathEncoder)
dumps = functools.partial(json.dumps, cls=_PathEncoder)
