from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Set, Union

from pydantic import BaseModel


class VT(IntEnum):
    Int = 0
    Float = 1
    Bool = 2
    Str = 3
    Bytes = 4
    Dict = 5
    List = 6
    Set = 7
    Datetime = 8
    Path = 9
    Model = 10


__I2VT: List[VT] = [
    VT.Int,
    VT.Float,
    VT.Bool,
    VT.Str,
    VT.Bytes,
    VT.Dict,
    VT.List,
    VT.Set,
    VT.Datetime,
    VT.Path,
    VT.Model,
]


def i2vt(i: int) -> VT:
    if 0 <= i <= 10:
        return __I2VT[i]
    raise ValueError(f"不存在ID为 {i} 的VT")


type ValidType = Union[
    int,
    float,
    bool,
    str,
    bytes,
    str,
    Dict[Any, Any],
    List[Any],
    Set[Any],
    datetime,
    Path,
    BaseModel,
]
