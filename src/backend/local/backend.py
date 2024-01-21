import shutil
from pathlib import Path
from typing import List, Literal, Self, Tuple, override

from src.const import StrPath
from src.const.exceptions import BackendError
from src.utils import Style, mkdir, run_sync

from ..backend import Backend, BackendResult
from .config import Config


class LocalBackend(Backend):
    root: Path

    @classmethod
    @override
    async def create(cls) -> Self:
        self = cls()
        self.root = cls.parse_config(Config).storage
        mkdir(self.root)
        return self

    @override
    async def _mkdir(self, path: StrPath) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        try:
            mkdir(self.root / path)
        except Exception as e:
            raise BackendError(f"创建文件夹时出错: {e!r}") from e

    @override
    async def _rmdir(self, path: StrPath) -> None:
        try:
            shutil.rmtree(self.root / path)
        except Exception as e:
            raise BackendError(f"删除文件夹时出错: {e!r}") from e

    @override
    async def _list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        try:
            return None, sorted(
                ("f" if p.is_file() else "d", p.name)
                for p in (self.root / path).iterdir()
            )
        except Exception as e:
            return BackendError(f"列出文件夹时出错: {e!r}"), []

    @override
    async def _get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        remote_fp = self.root / remote_fp

        if not remote_fp.exists():
            msg = f"远程文件 {Style.PATH_DEBUG(remote_fp)} 不存在"
            self.logger.debug(msg)
            return BackendError(msg)

        err = None
        for _ in range(max_try):
            try:
                with remote_fp.open("rb+") as fin, local_fp.open("wb") as fout:
                    read = run_sync(fin.read)
                    write = run_sync(fout.write)
                    while block := await read(4096):
                        await write(block)
                return
            except Exception as e:
                err = e
        msg = f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        return BackendError(msg)

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

        await self.mkdir(remote_fp.parent)
        remote = self.root / remote_fp
        mkdir(remote.parent)

        err = None
        for _ in range(max_try):
            try:
                with local_fp.open("rb+") as fin, remote.open("wb") as fout:
                    read = run_sync(fin.read)
                    write = run_sync(fout.write)
                    while block := await read(4096):
                        await write(block)

                return
            except Exception as e:
                err = e
        msg = f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        return BackendError(msg)

    @override
    async def _get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        err = None
        for _ in range(max_try):
            try:
                shutil.copytree(self.root / remote_fp, local_fp)
                return
            except Exception as e:
                err = e
        msg = f"下载目录 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        return BackendError(msg)

    @override
    async def _put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)

        if not local_fp.exists() or not local_fp.is_dir():
            msg = f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            return BackendError(msg)

        err = None
        for _ in range(max_try):
            try:
                shutil.copytree(local_fp, remote_fp)
                return
            except Exception as e:
                err = e
                shutil.rmtree(remote_fp)
        msg = f"上传 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        return BackendError(msg)
