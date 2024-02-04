# type: ignore
from base64 import b64decode
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Tuple, Type

from pydantic import BaseModel, Field

from .common import VT, ValidType, i2vt


def vt2t(vt: VT) -> Type[ValidType]:
    match vt:
        case VT.Int:
            return int
        case VT.Float:
            return float
        case VT.Bool:
            return bool
        case VT.Str:
            return str
        case VT.Bytes:
            return bytes
        case VT.Dict:
            return dict
        case VT.List:
            return list
        case VT.Set:
            return set
        case VT.Datetime:
            return datetime
        case VT.Path:
            return Path
        case VT.Model:
            return BaseModel


def ba2vt(b: bytearray) -> Tuple[VT, bytearray]:
    return i2vt(b[0]), b[1:]


def ba2int(b: bytearray) -> Tuple[int, bytearray]:
    length = b[0]
    value = 0
    for i in range(length, 0, -1):
        value = value * 256 + b[i]
    return value, b[length + 1 :]


def ba2float(b: bytearray) -> Tuple[float, bytearray]:
    length = b[0]
    precision = b[1]
    value = 0
    for i in range(length + 1, 1, -1):
        value = value * 256 + b[i]
    return value / (10**precision), b[length + 2 :]


def ba2bool(b: bytearray) -> Tuple[bool, bytearray]:
    return bool(b[0]), b[1:]


def ba2str(b: bytearray) -> Tuple[str, bytearray]:
    length, b = ba2int(b)
    return bytes(b[:length]).decode("utf-8"), b[length:]


def ba2bytes(b: bytearray) -> Tuple[bytes, bytearray]:
    length, b = ba2int(b)
    return b64decode(b[:length]), b[length:]


def ba2path(b: bytearray) -> Tuple[Path, bytearray]:
    s, b = ba2str(b)
    return Path(s), b


def ba2dict(b: bytearray) -> Tuple[dict, bytearray]:
    length, b = ba2int(b)
    parsed = {}

    for _ in range(length):
        vt, b = ba2vt(b)
        k, b = ByteArray2Value[vt](b)
        vt, b = ba2vt(b)
        v, b = ByteArray2Value[vt](b)
        parsed[k] = v

    return parsed, b


def ba2list(b: bytearray) -> Tuple[list, bytearray]:
    length, b = ba2int(b)
    parsed = []

    for _ in range(length):
        vt, b = ba2vt(b)
        v, b = ByteArray2Value[vt](b)
        parsed.append(v)

    return parsed, b


def ba2set(b: bytearray) -> Tuple[set, bytearray]:
    l, b = ba2list(b)
    return set(l), b


def ba2datetime(b: bytearray) -> Tuple[datetime, bytearray]:
    timestamp, b = ba2float(b)
    return datetime.fromtimestamp(timestamp), b


def ba2model(b: bytearray) -> Tuple[BaseModel, bytearray]:
    length, b = ba2int(b)
    model_name, b = ba2str(b)
    fields: Dict[str, Type[ValidType]] = {}
    parsed: Dict[str, ValidType] = {}

    for _ in range(length):
        field, b = ba2str(b)
        vt, b = ba2vt(b)
        value, b = ByteArray2Value[vt](b)
        fields[field] = vt2t(vt)
        parsed[field] = value

    attrs = {k: Field(default=parsed[k]) for k in fields} | {"__annotations__": fields}
    Model = type(model_name, (BaseModel,), attrs)
    return Model.model_validate(parsed), b


ByteArray2Value: Dict[VT, Callable[[bytearray], Tuple[ValidType, bytearray]]] = {
    VT.Int: ba2int,
    VT.Float: ba2float,
    VT.Bool: ba2bool,
    VT.Str: ba2str,
    VT.Bytes: ba2bytes,
    VT.Dict: ba2dict,
    VT.List: ba2list,
    VT.Set: ba2set,
    VT.Datetime: ba2datetime,
    VT.Path: ba2path,
    VT.Model: ba2model,
}
