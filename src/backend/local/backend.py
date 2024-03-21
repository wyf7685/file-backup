import shutil
from pathlib import Path
from typing import List, Literal, Self, Tuple, final, override

from src.const.exceptions import BackendError
from src.utils import Style, mkdir, run_sync

from ..backend import Backend
from ..config import parse_config
from .config import Config

config = parse_config(Config)


@final
class LocalBackend(Backend):
    root: Path
    CHUNK_SIZE: int = 4 * 1024 * 1024  # 4 MB

    @classmethod
    @override
    async def create(cls) -> Self:
        self = cls()
        self.root = mkdir(config.storage)
        return self

    @override
    async def _mkdir(self, path: Path) -> None:
        try:
            mkdir(self.root / path)
        except Exception as e:
            raise BackendError(f"创建文件夹时出错: {e!r}") from e

    @override
    async def _rmdir(self, path: Path) -> None:
        try:
            shutil.rmtree(self.root / path)
        except Exception as e:
            raise BackendError(f"删除文件夹时出错: {e!r}") from e

    @override
    async def _list_dir(
        self, path: Path = Path()
    ) -> List[Tuple[Literal["d", "f"], str]]:
        try:
            return sorted(
                ("f" if p.is_file() else "d", p.name)
                for p in (self.root / path).iterdir()
            )
        except Exception as e:
            raise BackendError(f"列出文件夹时出错: {e!r}") from e

    @override
    async def _get_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None:
        remote_fp = self.root / remote_fp

        if not remote_fp.exists():
            msg = f"远程文件 {Style.PATH_DEBUG(remote_fp)} 不存在"
            self.logger.debug(msg)
            raise BackendError(msg)

        err = None
        for _ in range(max_try):
            try:
                with remote_fp.open("rb+") as fin, local_fp.open("wb") as fout:
                    read = run_sync(fin.read)
                    write = run_sync(fout.write)
                    while block := await read(self.CHUNK_SIZE):
                        await write(block)
                return
            except Exception as e:
                err = e
        msg = f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        raise BackendError(msg) from err

    @override
    async def _put_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None:
        if not local_fp.is_file():
            msg = f"上传文件失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            raise BackendError(msg)

        await self.mkdir(remote_fp.parent)
        remote = self.root / remote_fp
        mkdir(remote.parent)

        err = None
        for _ in range(max_try):
            try:
                with local_fp.open("rb+") as fin, remote.open("wb") as fout:
                    read = run_sync(fin.read)
                    write = run_sync(fout.write)
                    while block := await read(self.CHUNK_SIZE):
                        await write(block)

                return
            except Exception as e:
                err = e
        msg = f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        raise BackendError(msg) from err

    @override
    async def _get_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None:
        err = None
        for _ in range(max_try):
            try:
                await run_sync(shutil.copytree)(self.root / remote_fp, local_fp)
                return
            except Exception as e:
                err = e
        msg = f"下载目录 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        raise BackendError(msg) from err

    @override
    async def _put_tree(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> None:
        if not local_fp.exists() or not local_fp.is_dir():
            msg = f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            raise BackendError(msg)

        err = None
        for _ in range(max_try):
            try:
                await run_sync(shutil.copytree)(local_fp, remote_fp)
                return
            except Exception as e:
                err = e
                shutil.rmtree(remote_fp)
        msg = f"上传 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        raise BackendError(msg) from err
