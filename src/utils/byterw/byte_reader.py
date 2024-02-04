from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Type

from pydantic import BaseModel

from .ba2value import ByteArray2Value, ba2vt
from .common import VT
from .crypt import decrypt


class ByteReader(object):
    __buffer: bytearray

    def __init__(self, buffer: bytes | bytearray, key: str | int | None = None) -> None:
        self.__buffer = bytearray(decrypt(buffer, key))

    def any(self):
        return len(self.__buffer) != 0

    def _read(self, vt: VT) -> Any:
        bvt, self.__buffer = ba2vt(self.__buffer)
        if vt != bvt:
            raise TypeError(f"预期读取 {vt}, 获取到 {bvt}")
        value, self.__buffer = ByteArray2Value[vt](self.__buffer)
        return value

    def read_int(self) -> int:
        return self._read(VT.Int)

    def read_float(self) -> float:
        return self._read(VT.Float)

    def read_bool(self) -> bool:
        return self._read(VT.Bool)

    def read_string(self) -> str:
        return self._read(VT.Str)

    def read_bytes(self) -> bytes:
        return self._read(VT.Bytes)

    def read_dict(self) -> Dict[Any, Any]:
        return self._read(VT.Dict)

    def read_list(self) -> List[Any]:
        return self._read(VT.List)

    def read_set(self) -> Set[Any]:
        return self._read(VT.Set)

    def read_datetime(self) -> datetime:
        return self._read(VT.Datetime)

    def read_path(self) -> Path:
        return self._read(VT.Path)

    def read_model[T: BaseModel](self, __T: Type[T] = BaseModel) -> T:
        return self._read(VT.Model)
