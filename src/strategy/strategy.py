from __future__ import annotations

import contextlib
import shutil
from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Self, override

import loguru

from src.backend import Backend, get_backend
from src.config import BackupConfig
from src.const import PATH
from src.const.exceptions import RestartBackup, StopBackup, StopOperation
from src.log import get_logger
from src.models import BackupRecord
from src.utils import ByteReader, ByteWriter, Style, get_uuid, mkdir, run_sync


class AbstractStrategy(metaclass=ABCMeta):
    logger: loguru.Logger

    @classmethod
    async def init(cls, config: BackupConfig) -> Self: ...

    @abstractmethod
    async def _make_backup(self) -> None: ...

    @abstractmethod
    async def _make_recovery(self, record: BackupRecord) -> Path: ...

    @abstractmethod
    async def make_backup(self) -> None: ...

    @abstractmethod
    async def make_recovery(self, record: BackupRecord) -> None: ...

    @abstractmethod
    async def prepare(self, *, miss_ok: bool = False) -> None: ...

    @abstractmethod
    def get_record(self, uuid: str) -> Optional[BackupRecord]: ...


class Strategy(AbstractStrategy):
    __strategy_name__: str = "Strategy"
    __prepared: bool
    __cache: Path
    client: Backend
    config: BackupConfig
    record: List[BackupRecord]

    @classmethod
    async def init(cls, config: BackupConfig) -> Self:
        self = cls.__new__(cls)
        self.config = config
        self.client = await get_backend().create()
        self.__cache = PATH.CACHE / get_uuid().split("-")[0]
        self.__prepared = False
        name = self.config.name
        self.logger = get_logger(cls.__strategy_name__, name).opt(colors=True)
        return self

    @property
    def CACHE(self) -> Path:
        return mkdir(self.__cache)

    @property
    def local(self) -> Path:
        return self.config.local_path

    @property
    def remote(self) -> Path:
        return self.config.remote

    def cache(self, uuid: str) -> Path:
        return mkdir(self.CACHE / uuid)

    async def load_record(self, *, miss_ok: bool = False) -> None:
        remote_fp = self.remote / "backup.7685"
        cache_fp = self.CACHE / "backup.7685"

        # 下载备份记录
        if err := await self.client.get_file(cache_fp, remote_fp):
            if not miss_ok:
                raise StopOperation("备份记录下载失败") from err
            self.logger.info("备份记录不存在, 正在创建...")
            self.record = []
            return

        data = cache_fp.read_bytes()
        cache_fp.unlink()
        self.record = ByteReader(data).read_list()

    async def add_record(self, uuid: str) -> None:
        """创建一个新备份

        Args:
            uuid (str): 本次备份的uuid
        """
        remote_fp = self.remote / "backup.7685"
        cache_fp = self.CACHE / "backup.7685"

        # 添加本次备份uuid
        now = datetime.now()
        self.record.append(
            BackupRecord(
                uuid=uuid,
                timestamp=now.timestamp(),
                timestr=now.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        self.record.sort(key=lambda x: x.timestamp)

        writer = ByteWriter()
        writer.write_list(self.record)
        cache_fp.write_bytes(writer.get())

        # 上传备份清单
        if err := await self.client.put_file(cache_fp, remote_fp):
            raise StopBackup("上传备份记录失败") from err
        cache_fp.unlink()

    def check_local(self) -> None:
        # 本地待备份路径错误
        if not self.local.exists():
            raise StopBackup(f"目标路径 {Style.PATH(self.local)} 不存在")

        if self.config.mode == "increment" and self.local.is_file():
            raise StopBackup("increment模式的路径不能是单个文件, 请使用compress模式")

    def check_uuid(self, uuid: str) -> None:
        if [i for i in self.record if i.uuid == uuid]:
            raise RestartBackup("uuid重复")

    async def prepare(self, *, miss_ok: bool = False) -> None:
        if self.__prepared:
            return

        await self.client.mkdir(self.remote)
        await self.load_record(miss_ok=miss_ok)
        self.__prepared = True

    def get_record(self, uuid: str) -> Optional[BackupRecord]:
        for record in self.record:
            if record.uuid == uuid:
                return record

    async def cleanup(self, uuid: Optional[str] = None) -> None:
        if uuid and hasattr(self, "client"):
            await self.client.rmdir(self.remote / uuid)

        with contextlib.suppress(Exception):
            del self.client
        shutil.rmtree(self.CACHE, True)

    async def _finish_recovery(self, result: Path) -> None:
        self.logger.info("备份下载完成，正在替换当前文件...")
        src, dst = Style.PATH_DEBUG(result), Style.PATH_DEBUG(self.local)
        self.logger.debug(f"移动文件夹: {src} -> {dst}")
        await run_sync(shutil.rmtree)(self.local)
        mkdir(self.local.parent)
        await run_sync(shutil.move)(result, self.local)

    @override
    async def make_backup(self) -> None:
        await self.prepare(miss_ok=True)
        try:
            await self._make_backup()
        except Exception as err:
            uuid = err.uuid if isinstance(err, StopOperation) else None
            await self.cleanup(uuid)
            raise err

    @override
    async def make_recovery(self, record: BackupRecord) -> None:
        await self.prepare(miss_ok=False)
        try:
            result = await self._make_recovery(record)
            await self._finish_recovery(result)
        finally:
            await self.cleanup()
