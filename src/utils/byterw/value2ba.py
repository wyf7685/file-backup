import functools
import typing
from base64 import b64encode
from datetime import datetime
from pathlib import Path
from types import UnionType, NoneType
from typing import Any, Callable, Dict, List, Set, TypeAliasType

from pydantic import BaseModel

from .common import VT, ValidType

__GA = (getattr(typing, "_GenericAlias"), getattr(typing, "_SpecialGenericAlias"))
__VTT = (int, float, str, bytes, dict, list, set, datetime, Path)  # type: ignore


@functools.cache
def t2vt(value: type) -> VT:
    if value is None or value is NoneType:
        return VT.Null

    if isinstance(value, __GA):
        value = getattr(value, "__origin__")
    elif isinstance(value, UnionType):
        value = getattr(value, "__args__")[0]
    elif isinstance(value, TypeAliasType):
        return VT.Str

    if issubclass(value, bool):
        return VT.Bool
    elif issubclass(value, __VTT):
        return getattr(VT, value.__name__.capitalize())
    elif issubclass(value, BaseModel):
        return VT.Model
    raise ValueError(f"{value!r} is not a valid ValueType")


def none2ba(_: None) -> bytearray:
    return bytearray([0])


def int2ba(value: int) -> bytearray:
    b = bytearray([value >= 0])
    value = abs(value)
    while value:
        b.append(value & 0xFF)
        value >>= 8
    b.insert(0, len(b) - 1)
    return b


def float2ba(value: float, precision: int = 10) -> bytearray:
    b = int2ba(round(value * (10**precision)))
    b.insert(1, precision)
    return b


def bool2ba(value: bool) -> bytearray:
    return bytearray([value])


def str2ba(value: str) -> bytearray:
    vb = value.encode("utf-8")
    b = bytearray()
    b.extend(int2ba(len(vb)))
    b.extend(vb)
    return b


def bytes2ba(value: bytes) -> bytearray:
    b = bytearray()
    value = b64encode(value)
    b.extend(int2ba(len(value)))
    b.extend(value)
    return b


def path2ba(value: Path) -> bytearray:
    return str2ba(value.as_posix())


def dict2ba(value: Dict[Any, Any]) -> bytearray:
    b = bytearray()
    b.extend(int2ba(len(value)))

    for k in sorted(value.keys()):
        kt = t2vt(type(k))
        b.append(int(kt))
        b.extend(Value2ByteArray[kt](k))
        v = value[k]
        vt = t2vt(type(v))
        b.append(int(vt))
        b.extend(Value2ByteArray[vt](v))

    return b


def list2ba(value: List[Any]) -> bytearray:
    b = bytearray()
    b.extend(int2ba(len(value)))

    for v in value:
        vt = t2vt(type(v))
        b.append(int(vt))
        b.extend(Value2ByteArray[vt](v))

    return b


def set2ba(value: Set[Any]) -> bytearray:
    return list2ba(list(value))


def datetime2ba(value: datetime) -> bytearray:
    return float2ba(value.timestamp(), 6)


def model2ba(value: BaseModel) -> bytearray:
    b = bytearray()
    b.extend(int2ba(len(value.model_fields)))
    b.extend(str2ba(value.__class__.__name__))

    for field in sorted(value.model_fields.keys()):
        anno = value.model_fields[field].annotation
        if anno is None:
            raise ValueError(f"Model {type(value)} field {field} has no annotation")

        vt = t2vt(anno)
        b.extend(str2ba(field))
        b.append(int(vt))
        b.extend(Value2ByteArray[vt](getattr(value, field)))

    return b


Value2ByteArray: Dict[VT, Callable[[Any], bytearray]] = {
    VT.Null: none2ba,
    VT.Int: int2ba,
    VT.Float: float2ba,
    VT.Bool: bool2ba,
    VT.Str: str2ba,
    VT.Bytes: bytes2ba,
    VT.Dict: dict2ba,
    VT.List: list2ba,
    VT.Set: set2ba,
    VT.Datetime: datetime2ba,
    VT.Path: path2ba,
    VT.Model: model2ba,
}


def value2ba(value: ValidType) -> bytearray:
    return Value2ByteArray[t2vt(type(value))](value)
