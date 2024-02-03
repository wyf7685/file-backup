from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Union, Any, Dict, List, Set

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


def i2vt(i: int) -> VT:
    match i:
        case 0:
            return VT.Int
        case 1:
            return VT.Float
        case 2:
            return VT.Bool
        case 3:
            return VT.Str
        case 4:
            return VT.Bytes
        case 5:
            return VT.Dict
        case 6:
            return VT.List
        case 7:
            return VT.Set
        case 8:
            return VT.Datetime
        case 9:
            return VT.Path
        case 10:
            return VT.Model
        case _:
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
