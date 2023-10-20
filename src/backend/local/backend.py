import shutil
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple

import aiofiles

from src.const import StrPath
from src.utils import Style, mkdir

from ..backend import Backend

if TYPE_CHECKING:
    from src.log import Logger


class LocalBackend(Backend):
    local_root: Path
    logger: "Logger"

    def __init__(self) -> None:
        from src.models import config

        super(LocalBackend, self).__init__()
        self.local_root = config.backend.local.storage

    async def mkdir(self, path: StrPath) -> None:
        await super(LocalBackend, self).mkdir(path)
        if not isinstance(path, Path):
            path = Path(path)
        mkdir(self.local_root / path)

    async def rmdir(self, path: StrPath) -> None:
        await super(LocalBackend, self).rmdir(path)
        shutil.rmtree(self.local_root / path)

    async def list_dir(self, path: StrPath = ".") -> List[Tuple[str, str]]:
        await super(LocalBackend, self).list_dir(path)
        return sorted(
            ("f" if p.is_file() else "d", p.name)
            for p in (self.local_root / path).iterdir()
        )

    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(LocalBackend, self).get_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        remote_fp = self.local_root / remote_fp

        if not remote_fp.exists():
            self.logger.debug(f"远程文件 {remote_fp} 不存在")
            return False

        err = None
        for _ in range(max_try):
            try:
                async with aiofiles.open(remote_fp, "rb+") as f:
                    data = await f.read()

                async with aiofiles.open(local_fp, "wb") as f:
                    await f.write(data)

                return True
            except Exception as e:
                err = e
        self.logger.debug(f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}")
        return False

    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(LocalBackend, self).put_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, Path) and not local_fp.is_file():
            self.logger.debug(f"上传文件失败: {Style.PATH_DEBUG(local_fp)} 不存在")
            return False

        await self.mkdir(remote_fp.parent)

        err = None
        for _ in range(max_try):
            try:
                async with aiofiles.open(local_fp, "rb+") as f:
                    data = await f.read()

                async with aiofiles.open(self.local_root / remote_fp, "wb") as f:
                    await f.write(data)

                return True
            except Exception as e:
                err = e
        self.logger.debug(f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {Style.RED(err)}")
        return False

    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(LocalBackend, self).get_tree(local_fp, remote_fp, max_try)

        err = None
        for _ in range(max_try):
            try:
                shutil.copytree(self.local_root / remote_fp, local_fp)
                return True
            except Exception as e:
                err = e
        self.logger.debug(f"下载目录 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}")
        return False

    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(LocalBackend, self).put_tree(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)

        if not local_fp.exists() or not local_fp.is_dir():
            self.logger.debug(f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在")
            return False

        err = None
        for _ in range(max_try):
            try:
                shutil.copytree(local_fp, remote_fp)
                return True
            except Exception as e:
                err = e
                shutil.rmtree(remote_fp)
        self.logger.debug(f"上传 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}")
        return False
