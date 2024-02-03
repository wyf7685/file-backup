from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Self

from pydantic import BaseModel

from .common import VT
from .crypt import encrypt
from .value2ba import (
    bool2ba,
    bytes2ba,
    datetime2ba,
    dict2ba,
    float2ba,
    int2ba,
    list2ba,
    model2ba,
    set2ba,
    str2ba,
)


class ByteWriter(object):
    __buffer: bytearray

    def __init__(self):
        self.__buffer = bytearray()

    def get(self) -> bytes:
        return encrypt(bytes(self.__buffer))

    def _write(self, value: bytes | bytearray) -> None:
        self.__buffer.extend(value)

    def _write_sign(self, value: VT) -> None:
        b = bytearray()
        b.append(int(value))
        self._write(b)

    def write_int(self, value: int) -> Self:
        self._write_sign(VT.Int)
        self._write(int2ba(value))
        return self

    def write_float(self, value: float, precision: int = 10) -> Self:
        self._write_sign(VT.Float)
        self._write(float2ba(value, precision))
        return self

    def write_bool(self, value: bool) -> Self:
        self._write_sign(VT.Bool)
        self._write(bool2ba(value))
        return self

    def write_string(self, value: str) -> Self:
        self._write_sign(VT.Str)
        self._write(str2ba(value))
        return self

    def write_bytes(self, value: bytes) -> Self:
        self._write_sign(VT.Bytes)
        self._write(bytes2ba(value))
        return self

    def write_dict(self, value: Dict[Any, Any]) -> Self:
        self._write_sign(VT.Dict)
        self._write(dict2ba(value))
        return self

    def write_list(self, value: List[Any]) -> Self:
        self._write_sign(VT.List)
        self._write(list2ba(value))
        return self

    def write_set(self, value: Set[Any]) -> Self:
        self._write_sign(VT.Set)
        self._write(set2ba(value))
        return self

    def write_datetime(self, value: datetime) -> Self:
        self._write_sign(VT.Datetime)
        self._write(datetime2ba(value))
        return self

    def write_path(self, value: Path) -> Self:
        self._write_sign(VT.Path)
        self._write(str2ba(value.as_posix()))
        return self

    def write_model(self, value: BaseModel) -> Self:
        self._write_sign(VT.Model)
        self._write(model2ba(value))
        return self
