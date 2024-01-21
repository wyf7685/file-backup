from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, List, Literal, Optional, Self, Set, Tuple, Type, override

from src.const import StrPath
from src.const.exceptions import BackendError
from src.log import get_logger
from src.utils import Style

from .config import parse_config

if TYPE_CHECKING:
    from src.log import Logger

type BackendResult = Optional[BackendError]


def _color(path: StrPath) -> str:
    return Style.PATH_DEBUG(path)


class BaseBackend(metaclass=ABCMeta):
    logger: "Logger"

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__).opt(colors=True)

    @staticmethod
    def parse_config[T](config_cls: Type[T]) -> T:
        return parse_config(config_cls)

    @classmethod
    @abstractmethod
    async def create(cls) -> Self:
        ...

    @abstractmethod
    async def mkdir(self, path: StrPath) -> None:
        ...

    @abstractmethod
    async def rmdir(self, path: StrPath) -> None:
        ...

    @abstractmethod
    async def list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        ...

    @abstractmethod
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @abstractmethod
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @abstractmethod
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @abstractmethod
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...


class Backend(BaseBackend):
    __mkdir_cache: Set[StrPath]

    def __init__(self):
        super().__init__()
        self.__mkdir_cache = set()

    @abstractmethod
    async def _mkdir(self, path: StrPath) -> None:
        ...

    @abstractmethod
    async def _rmdir(self, path: StrPath) -> None:
        ...

    @abstractmethod
    async def _list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        ...

    @abstractmethod
    async def _get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @abstractmethod
    async def _put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @abstractmethod
    async def _get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @abstractmethod
    async def _put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        ...

    @classmethod
    @override
    async def create(cls) -> Self:
        return cls()

    @override
    async def mkdir(self, path: StrPath) -> None:
        if path in self.__mkdir_cache:
            return
        self.__mkdir_cache.add(path)
        self.logger.debug(f"创建目录: {_color(path)}")

    @override
    async def rmdir(self, path: StrPath) -> None:
        self.logger.debug(f"删除目录: {_color(path)}")

    @override
    async def list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        self.logger.debug(f"列出目录: {_color(path)}")
        return await self._list_dir(path)

    @override
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        self.logger.debug(f"下载文件: {_color(remote_fp)} -> {_color(local_fp)}")
        return await self._get_file(local_fp, remote_fp, max_try)

    @override
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        self.logger.debug(f"上传文件: {_color(local_fp)} -> {_color(remote_fp)}")
        return await self._put_file(local_fp, remote_fp, max_try)

    @override
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        self.logger.debug(f"下载目录: {_color(remote_fp)} -> {_color(local_fp)}")
        return await self._get_tree(local_fp, remote_fp, max_try)

    @override
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        self.logger.debug(f"上传目录: {_color(local_fp)} -> {_color(remote_fp)}")
        return await self._put_tree(local_fp, remote_fp, max_try)
