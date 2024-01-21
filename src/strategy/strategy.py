import contextlib
import json
import shutil
from abc import ABCMeta, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple, Type, override

from src.backend import Backend, get_backend
from src.config import BackupConfig
from src.const import PATH
from src.const.exceptions import RestartBackup, StopBackup, StopOperation
from src.log import get_logger
from src.models import BackupRecord
from src.utils import Style, get_uuid, mkdir, run_sync

if TYPE_CHECKING:
    from src.log import Logger


class BaseStrategy(metaclass=ABCMeta):
    logger: "Logger"
    config: BackupConfig
    _backend: Type[Backend]
    _cache: Path
    client: Backend
    record: List[BackupRecord]

    @abstractmethod
    async def _on_init(self):
        ...

    @abstractmethod
    async def _make_backup(self) -> None:
        ...

    @abstractmethod
    async def _make_recovery(self, record: BackupRecord) -> Tuple[str, Path]:
        ...

    @abstractmethod
    async def make_backup(self) -> None:
        ...

    @abstractmethod
    async def make_recovery(self, record: BackupRecord) -> None:
        ...


class Strategy(BaseStrategy):
    def __init__(self, config: BackupConfig):
        self.config = config
        self._backend = get_backend()
        self._cache = PATH.CACHE / get_uuid().split("-")[0]
        name = self.config.name
        self.logger = get_logger(name).opt(colors=True)

    @classmethod
    async def init(cls, config: BackupConfig):
        self = cls(config)
        await self._on_init()
        return self

    @property
    def CACHE(self) -> Path:
        return mkdir(self._cache)

    @property
    def local(self) -> Path:
        return self.config.local_path

    @property
    def remote(self) -> Path:
        return self.config.get_remote()

    def cache(self, uuid: str) -> Path:
        return mkdir(self.CACHE / uuid)

    async def load_record(self, miss_ok: bool = False) -> None:
        remote_fp = self.remote / "backup.json"
        cache_fp = self.CACHE / "backup.json"

        # 下载备份记录
        if not await self.client.get_file(cache_fp, remote_fp):
            if not miss_ok:
                raise StopOperation("备份记录下载失败")
            self.logger.info("备份记录不存在, 正在创建...")
            cache_fp.write_text("[]")

        raw = cache_fp.read_text()
        cache_fp.unlink()
        self.record = [BackupRecord.model_validate(i) for i in json.loads(raw)]

    async def add_record(self, uuid: str) -> None:
        """创建一个新备份

        Args:
            uuid (str): 本次备份的uuid
        """
        now = datetime.now()
        remote_fp = self.remote / "backup.json"
        cache_fp = self.CACHE / "backup.json"

        # 添加本次备份uuid
        self.record.append(
            BackupRecord(
                uuid=uuid,
                timestamp=now.timestamp(),
                timestr=now.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        self.record.sort(key=lambda x: x.timestamp)
        cache_fp.write_text(
            json.dumps(
                [json.loads(record.model_dump_json()) for record in self.record],
                indent=4,
            ),
            encoding="utf-8",
        )

        # 上传备份清单
        if not await self.client.put_file(cache_fp, remote_fp):
            raise StopBackup("上传备份记录失败")
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

    async def prepare(self, miss_ok: bool = False) -> None:
        self.client = await self._backend.create()
        await self.client.mkdir(str(self.remote))
        await self.load_record(miss_ok=miss_ok)

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

    async def _finish_recovery(self, uuid: str, result: Path) -> None:
        self.logger.info("备份下载完成，正在替换当前文件...")
        self.logger.debug(
            f"移动文件夹: {Style.PATH_DEBUG(result)} -> {Style.PATH_DEBUG(self.local)}"
        )
        await run_sync(shutil.rmtree)(self.local)
        mkdir(self.local.parent)
        await run_sync(shutil.move)(result, self.local)
        self.logger.success(f"备份 [{Style.CYAN(uuid)}] 恢复完成!")

    @override
    async def make_backup(self) -> None:
        await self.prepare(miss_ok=True)
        try:
            await self._make_backup()
        except StopOperation as err:
            if err.uuid:
                await self.cleanup(err.uuid)
            raise err
        except Exception as err:
            await self.cleanup()
            raise err

    @override
    async def make_recovery(self, record: BackupRecord) -> None:
        await self.prepare()
        uuid, result = None, None
        try:
            uuid, result = await self._make_recovery(record)
        finally:
            if uuid and result:
                await self._finish_recovery(uuid, result)
            await self.cleanup()
