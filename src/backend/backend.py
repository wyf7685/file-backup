from typing import TYPE_CHECKING, Any, List, Tuple, Self

import aiofiles as _

from src.const import *
from src.log import get_logger
from src.utils import Style

if TYPE_CHECKING:
    from src.log import Logger


def _color(path: Any) -> str:
    return Style.PATH_DEBUG(path)


class Backend(object):
    logger: "Logger"

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__).opt(colors=True)
    
    @classmethod
    async def create(cls) -> Self:
        return cls()

    async def mkdir(self, path: StrPath) -> None:
        self.logger.debug(f"创建目录: {_color(path)}")

    async def rmdir(self, path: StrPath) -> None:
        self.logger.debug(f"删除目录: {_color(path)}")

    async def list_dir(self, path: StrPath = ".") -> List[Tuple[str, str]]:
        self.logger.debug(f"列出目录: {_color(path)}")
        return []

    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        self.logger.debug(f"下载文件: {_color(remote_fp)} -> {_color(local_fp)}")
        return True

    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        self.logger.debug(f"上传文件: {_color(local_fp)} -> {_color(remote_fp)}")
        return True

    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        self.logger.debug(f"下载目录: {_color(remote_fp)} -> {_color(local_fp)}")
        return True

    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        self.logger.debug(f"上传目录: {_color(local_fp)} -> {_color(remote_fp)}")
        return True
