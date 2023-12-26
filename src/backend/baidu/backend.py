from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple, override

from src.const import StrPath
from src.models import BaiduConfig
from src.utils import Style
from src.utils import mkdir as local_mkdir

from ..backend import Backend
from .sdk import get_file, list_dir, mkdir, put_file, refresh_access_token
from .sdk.exceptions import BaiduError

if TYPE_CHECKING:
    from src.log import Logger


class BaiduBackend(Backend):
    config: BaiduConfig
    logger: "Logger"

    @override
    def __init__(self) -> None:
        from src.models import config

        super(BaiduBackend, self).__init__()
        self.config = config.backend.baidu

    @override
    @classmethod
    async def create(cls):
        self = await super().create()
        await refresh_access_token()
        return self

    @override
    async def mkdir(self, path: StrPath) -> None:
        await super(BaiduBackend, self).mkdir(path)
        if not isinstance(path, Path):
            path = Path(path)

        await mkdir(path)

    @override
    async def rmdir(self, path: StrPath) -> None:
        await super(BaiduBackend, self).rmdir(path)
        # rmdir
        raise NotImplemented

    @override
    async def list_dir(self, path: StrPath = ".") -> List[Tuple[str, str]]:
        await super(BaiduBackend, self).list_dir(path)

        if isinstance(path, str):
            path = Path(path)

        try:
            return sorted(await list_dir(path))
        except BaiduError as err:
            self.logger.debug(err)
            return []

    @override
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(BaiduBackend, self).get_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        err = None
        for _ in range(max_try):
            try:
                await get_file(local_fp, remote_fp)
                return True
            except Exception as e:
                err = e
        self.logger.debug(f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常")
        self.logger.debug(err)
        return False

    @override
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(BaiduBackend, self).put_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, Path) and not local_fp.is_file():
            self.logger.debug(f"上传文件失败: {Style.PATH_DEBUG(local_fp)} 不存在")
            return False

        err = None
        for _ in range(max_try):
            try:
                await put_file(local_fp, remote_fp)
                return True
            except BaiduError as e:
                err = e
        self.logger.debug(f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常")
        self.logger.debug(err)
        return False

    @override
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(BaiduBackend, self).get_tree(local_fp, remote_fp, max_try)

        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)

        for t, name in await self.list_dir(remote_fp):
            local = local_fp / name
            remote = remote_fp / name
            if t == "d":
                if not await self.get_tree(local_mkdir(local), remote, max_try):
                    return False
            elif t == "f":
                if not await self.get_file(local, remote, max_try):
                    return False

        return True

    @override
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(BaiduBackend, self).put_tree(local_fp, remote_fp, max_try)

        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if not local_fp.exists() or not local_fp.is_dir():
            self.logger.debug(f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在")
            return False

        for p in local_fp.iterdir():
            if p.is_dir():
                await self.mkdir(remote_fp / p.name)
                if not await self.put_tree(p, remote_fp / p.name, max_try):
                    return False
            elif p.is_file():
                if not await self.put_file(p, remote_fp / p.name, max_try):
                    return False

        return True
