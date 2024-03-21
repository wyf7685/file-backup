from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Literal, Optional, Self, Set, Tuple, Type, override

import loguru

from src.const import StrPath
from src.const.exceptions import BackendError
from src.log import get_logger
from src.utils import Style, get_frame, mkdir

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
        self, path: StrPath = Path()
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]: ...

    @abstractmethod
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult: ...

    @abstractmethod
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult: ...


class Backend(AbstractBackend):
    __mkdir_cache: Set[Path]

    @override
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__).opt(colors=True)
        self.__mkdir_cache = set()
        self_r = Style.BLUE(repr(self))
        self._logger.bind(head="create").debug(f"创建实例: {self_r}")

    def __del__(self) -> None:
        self_r = Style.BLUE(repr(self))
        self._logger.bind(head="delete").debug(f"销毁实例: {self_r}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

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
    ) -> List[Tuple[Literal["d", "f"], str]]: ...

    @abstractmethod
    async def _get_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None: ...

    @abstractmethod
    async def _put_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None: ...

    async def _get_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None:
        err, res = await self.list_dir(remote_fp)
        if err:
            raise err

        for t, name in res:
            local = local_fp / name
            remote = remote_fp / name
            if t == "d":
                if err := await self.get_tree(mkdir(local), remote, max_try):
                    raise err
            elif t == "f":
                if err := await self.get_file(local, remote, max_try):
                    raise err

    async def _put_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None:
        if not local_fp.exists() or not local_fp.is_dir():
            msg = f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            raise BackendError(msg)

        for p in local_fp.iterdir():
            if p.is_dir():
                await self.mkdir(remote_fp / p.name)
                if err := await self.put_tree(p, remote_fp / p.name, max_try):
                    raise err
            elif p.is_file():
                if err := await self.put_file(p, remote_fp / p.name, max_try):
                    raise err

    @classmethod
    @override
    async def create(cls) -> Self:
        return cls()

    @override
    async def mkdir(self, path: StrPath) -> None:
        if isinstance(path, str):
            path = Path(path)
        if path in self.__mkdir_cache:
            return
        self.__mkdir_cache.add(path)
        self.logger.debug(f"创建目录: {_color(path)}")
        await self._mkdir(path)

    @override
    async def rmdir(self, path: StrPath) -> None:
        if isinstance(path, str):
            path = Path(path)
        self.logger.debug(f"删除目录: {_color(path)}")
        await self._rmdir(path)

    @override
    async def list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        if isinstance(path, str):
            path = Path(path)
        self.logger.debug(f"列出目录: {_color(path)}")
        try:
            return None, await self._list_dir(path)
        except BackendError as err:
            return err, []

    @override
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"下载文件: {_color(remote_fp)} -> {_color(local_fp)}")

        try:
            await self._get_file(local_fp, remote_fp, max_try)
        except BackendError as err:
            return err

    @override
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"上传文件: {_color(local_fp)} -> {_color(remote_fp)}")

        try:
            await self._put_file(local_fp, remote_fp, max_try)
        except BackendError as err:
            return err

    @override
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"下载目录: {_color(remote_fp)} -> {_color(local_fp)}")

        try:
            await self._get_tree(local_fp, remote_fp, max_try)
        except BackendError as err:
            return err

    @override
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        self.logger.debug(f"上传目录: {_color(local_fp)} -> {_color(remote_fp)}")

        try:
            await self._put_tree(local_fp, remote_fp, max_try)
        except BackendError as err:
            return err
