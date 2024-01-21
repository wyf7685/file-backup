from pathlib import Path
from typing import List, Literal, Tuple, override

from src.const import StrPath
from src.utils import Style
from src.utils import mkdir as local_mkdir

from ..backend import Backend, BackendResult
from .sdk import get_file, list_dir, mkdir, put_file, refresh_access_token
from .sdk.exceptions import BackendError, BaiduError


class BaiduBackend(Backend):
    @override
    @classmethod
    async def create(cls):  # sourcery skip: inline-immediately-returned-variable
        self = await super().create()
        # await refresh_access_token()
        return self

    @override
    async def _mkdir(self, path: StrPath) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        await mkdir(path)

    @override
    async def _rmdir(self, path: StrPath) -> None:
        # raise NotImplemented
        ...

    @override
    async def _list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        if isinstance(path, str):
            path = Path(path)

        try:
            return None, sorted(await list_dir(path))
        except BaiduError as err:
            self.logger.debug(err)
            return BackendError(f"列出文件夹时出现错误: {err}"), []

    @override
    async def _get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        err = None
        for _ in range(max_try):
            try:
                await get_file(local_fp, remote_fp)
                return
            except BaiduError as e:
                err = e
        self.logger.debug(f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常")
        self.logger.debug(err)
        return err

    @override
    async def _put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, Path) and not local_fp.is_file():
            msg = f"上传文件失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            return BackendError(msg)

        err = None
        for _ in range(max_try):
            try:
                await put_file(local_fp, remote_fp)
                return
            except BaiduError as e:
                err = e
        self.logger.debug(f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常")
        self.logger.debug(err)
        return BackendError(f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {err}")

    @override
    async def _get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)

        err, res = await self.list_dir(remote_fp)
        if err:
            return err

        for t, name in res:
            local = local_fp / name
            remote = remote_fp / name
            if t == "d":
                if err := await self.get_tree(local_mkdir(local), remote, max_try):
                    return err
            elif t == "f":
                if err := await self.get_file(local, remote, max_try):
                    return err

    @override
    async def _put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if not local_fp.exists() or not local_fp.is_dir():
            msg = f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            return BackendError(msg)

        for p in local_fp.iterdir():
            if p.is_dir():
                await self.mkdir(remote_fp / p.name)
                if err := await self.put_tree(p, remote_fp / p.name, max_try):
                    return err
            elif p.is_file():
                if err := await self.put_file(p, remote_fp / p.name, max_try):
                    return err
