from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Set, Union
from types import NoneType

from pydantic import BaseModel

type ValidType = Union[
    NoneType,
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


class VT(IntEnum):
    Null = 0
    Int = 1
    Float = 2
    Bool = 3
    Str = 4
    Bytes = 5
    Dict = 6
    List = 7
    Set = 8
    Datetime = 9
    Path = 10
    Model = 11


__I2VT: List[VT] = [
    VT.Null,
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
    if 0 <= i <= 11:
        return __I2VT[i]
    raise ValueError(f"不存在ID为 {i} 的VT")
