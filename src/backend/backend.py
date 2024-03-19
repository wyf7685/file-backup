from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Literal, Optional, Self, Set, Tuple, Type, override

import loguru

from src.const import StrPath
from src.const.exceptions import BackendError
from src.log import get_logger
from src.utils import Style, get_frame

from .config import parse_config

type BackendResult = Optional[BackendError]


def _color(path: StrPath) -> str:
    return Style.PATH_DEBUG(path)


class AbstractBackend(metaclass=ABCMeta):
    _logger: loguru.Logger

    @abstractmethod
    def __init__(self): ...

    @classmethod
    @abstractmethod
    async def create(cls) -> Self: ...

    @abstractmethod
    async def mkdir(self, path: StrPath) -> None: ...

    @abstractmethod
    async def rmdir(self, path: StrPath) -> None: ...

    @abstractmethod
    async def list_dir(
        self, path: Path = Path()
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]: ...

    @abstractmethod
    async def get_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def put_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def get_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def put_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...


class Backend(AbstractBackend):
    __mkdir_cache: Set[Path]

    @override
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__).opt(colors=True)
        self.__mkdir_cache = set()
        self_r = Style.BLUE(repr(self), False)
        self._logger.bind(head="create").debug(f"Create instance: {self_r}")

    def __del__(self) -> None:
        self_r = Style.BLUE(repr(self), False)
        self._logger.bind(head="delete").debug(f"Destroy instance: {self_r}")

    @property
    def logger(self) -> loguru.Logger:
        return self._logger.bind(head=get_frame(1).f_code.co_name)

    @staticmethod
    def _parse_config[T](config_cls: Type[T]) -> T:
        return parse_config(config_cls)

    @abstractmethod
    async def _mkdir(self, path: Path) -> None: ...

    @abstractmethod
    async def _rmdir(self, path: Path) -> None: ...

    @abstractmethod
    async def _list_dir(
        self, path: Path = Path()
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]: ...

    @abstractmethod
    async def _get_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def _put_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def _get_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def _put_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult: ...

    @classmethod
    @override
    async def create(cls) -> Self:
        return cls()

    @override
    async def mkdir(self, path: StrPath) -> None:
        if path in self.__mkdir_cache:
            return
        if isinstance(path, str):
            path = Path(path)
        self.__mkdir_cache.add(path)
        self.logger.debug(f"创建目录: {_color(path)}")

    @override
    async def rmdir(self, path: StrPath) -> None:
        if isinstance(path, str):
            path = Path(path)
        self.logger.debug(f"删除目录: {_color(path)}")

    @override
    async def list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        if isinstance(path, str):
            path = Path(path)
        self.logger.debug(f"列出目录: {_color(path)}")
        return await self._list_dir(path)

    @override
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"下载文件: {_color(remote_fp)} -> {_color(local_fp)}")
        return await self._get_file(local_fp, remote_fp, max_try)

    @override
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"上传文件: {_color(local_fp)} -> {_color(remote_fp)}")
        return await self._put_file(local_fp, remote_fp, max_try)

    @override
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"下载目录: {_color(remote_fp)} -> {_color(local_fp)}")
        return await self._get_tree(local_fp, remote_fp, max_try)

    @override
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"上传目录: {_color(local_fp)} -> {_color(remote_fp)}")
        return await self._put_tree(local_fp, remote_fp, max_try)
