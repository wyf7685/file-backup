import shutil
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple, override

from src.const import StrPath
from src.utils import Style, mkdir, run_sync

from ..backend import Backend

if TYPE_CHECKING:
    from src.log import Logger


class LocalBackend(Backend):
    root: Path
    logger: "Logger"

    @override
    def __init__(self) -> None:
        from src.models import config

        super(LocalBackend, self).__init__()
        self.root = config.backend.local.storage

    @override
    async def mkdir(self, path: StrPath) -> None:
        await super(LocalBackend, self).mkdir(path)
        if not isinstance(path, Path):
            path = Path(path)
        mkdir(self.root / path)

    @override
    async def rmdir(self, path: StrPath) -> None:
        await super(LocalBackend, self).rmdir(path)
        shutil.rmtree(self.root / path)

    @override
    async def list_dir(self, path: StrPath = ".") -> List[Tuple[str, str]]:
        await super(LocalBackend, self).list_dir(path)
        return sorted(
            ("f" if p.is_file() else "d", p.name) for p in (self.root / path).iterdir()
        )

    @override
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(LocalBackend, self).get_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        remote_fp = self.root / remote_fp

        if not remote_fp.exists():
            self.logger.debug(f"远程文件 {remote_fp} 不存在")
            return False

        err = None
        for _ in range(max_try):
            try:
                with remote_fp.open("rb+") as fin, local_fp.open("wb") as fout:
                    read = run_sync(fin.read)
                    write = run_sync(fout.write)
                    while block := await read(4096):
                        await write(block)
                return True
            except Exception as e:
                err = e
        self.logger.debug(f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}")
        return False

    @override
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
        remote = self.root / remote_fp

        err = None
        for _ in range(max_try):
            try:
                with local_fp.open("rb+") as fin, remote.open("wb") as fout:
                    read = run_sync(fin.read)
                    write = run_sync(fout.write)
                    while block := await read(4096):
                        await write(block)

                return True
            except Exception as e:
                err = e
        self.logger.debug(f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {Style.RED(err)}")
        return False

    @override
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(LocalBackend, self).get_tree(local_fp, remote_fp, max_try)

        err = None
        for _ in range(max_try):
            try:
                shutil.copytree(self.root / remote_fp, local_fp)
                return True
            except Exception as e:
                err = e
        self.logger.debug(f"下载目录 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}")
        return False

    @override
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
