from base64 import b64decode
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Tuple, Type, List, Set, Any

from pydantic import BaseModel, Field

from .common import VT, ValidType


__VT2T: Dict[VT, Type[ValidType] | None] = {
    VT.Null: None,
    VT.Int: int,
    VT.Float: float,
    VT.Bool: bool,
    VT.Str: str,
    VT.Bytes: bytes,
    VT.Dict: Dict[Any, Any],
    VT.List: List[Any],
    VT.Set: Set[Any],
    VT.Datetime: datetime,
    VT.Path: Path,
    VT.Model: BaseModel,
}


def mv2vt(m: memoryview) -> Tuple[VT, memoryview]:
    return VT.from_bytes(m[:1]), m[1:]


def mv2none(m: memoryview) -> Tuple[None, memoryview]:
    return None, m[1:]


def mv2int(m: memoryview) -> Tuple[int, memoryview]:
    length = m[0]
    return int.from_bytes(m[1 : length + 1], signed=True), m[length + 1 :]


def mv2float(m: memoryview) -> Tuple[float, memoryview]:
    length, precision = m[:2]
    value = int.from_bytes(m[2 : length + 2], signed=True)
    return value / (10**precision), m[length + 2 :]


def mv2bool(m: memoryview) -> Tuple[bool, memoryview]:
    return bool(m[0]), m[1:]


def mv2str(m: memoryview) -> Tuple[str, memoryview]:
    length, m = mv2int(m)
    return m[:length].tobytes().decode("utf-8"), m[length:]


def mv2bytes(m: memoryview) -> Tuple[bytes, memoryview]:
    length, m = mv2int(m)
    return b64decode(m[:length].tobytes()), m[length:]


def mv2path(m: memoryview) -> Tuple[Path, memoryview]:
    string, m = mv2str(m)
    return Path(string), m


def mv2dict(m: memoryview) -> Tuple[Dict[Any, Any], memoryview]:
    length, m = mv2int(m)
    parsed: Dict[Any, Any] = {}

    for _ in range(length):
        vt, m = mv2vt(m)
        k, m = MemoryView2Value[vt](m)
        vt, m = mv2vt(m)
        v, m = MemoryView2Value[vt](m)
        parsed[k] = v

    return parsed, m


def mv2list(m: memoryview) -> Tuple[List[Any], memoryview]:
    length, m = mv2int(m)
    parsed: List[Any] = []

    for _ in range(length):
        vt, m = mv2vt(m)
        v, m = MemoryView2Value[vt](m)
        parsed.append(v)

    return parsed, m


def mv2set(m: memoryview) -> Tuple[Set[Any], memoryview]:
    parsed, m = mv2list(m)
    return set(parsed), m


def mv2datetime(m: memoryview) -> Tuple[datetime, memoryview]:
    timestamp, m = mv2float(m)
    return datetime.fromtimestamp(timestamp), m


def mv2model(m: memoryview) -> Tuple[BaseModel, memoryview]:
    length, m = mv2int(m)
    model_name, m = mv2str(m)
    fields: Dict[str, Type[ValidType] | None] = {}
    parsed: Dict[str, ValidType] = {}

    for _ in range(length):
        field, m = mv2str(m)
        vt, m = mv2vt(m)
        value, m = MemoryView2Value[vt](m)
        fields[field] = __VT2T[vt]
        parsed[field] = value

    attrs = {k: Field(default=parsed[k]) for k in fields} | {"__annotations__": fields}
    Model = type(model_name, (BaseModel,), attrs)
    return Model.model_validate(parsed), m


MemoryView2Value: Dict[VT, Callable[[memoryview], Tuple[ValidType, memoryview]]] = {
    VT.Null: mv2none,
    VT.Int: mv2int,
    VT.Float: mv2float,
    VT.Bool: mv2bool,
    VT.Str: mv2str,
    VT.Bytes: mv2bytes,
    VT.Dict: mv2dict,
    VT.List: mv2list,
    VT.Set: mv2set,
    VT.Datetime: mv2datetime,
    VT.Path: mv2path,
    VT.Model: mv2model,
}
