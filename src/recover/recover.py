import json
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Tuple, Type

from src.backend import Backend, get_backend
from src.const import PATH
from src.const.exceptions import StopRecovery
from src.log import get_logger
from src.models import *
from src.utils import compress_password, mkdir, unpack_7zip

if TYPE_CHECKING:
    from src.log import Logger


class Recover(object):
    config: BackupConfig
    logger: "Logger"
    client: Backend
    records: List[BackupRecord]
    _backend: Type[Backend]
    _cache: Path

    def __init__(self, config: BackupConfig) -> None:
        self.config = config
        self.logger = get_logger(self.config.name).opt(colors=True)
        self._backend = get_backend()
        self._cache = PATH.CACHE / "recovery" / self.config.name

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name})"

    async def load_record_list(self) -> None:
        client = self._backend()
        remote_fp = self.remote / "backup.json"
        cache_fp = self.CACHE / "backup.json"

        if not await client.get_file(cache_fp, remote_fp):
            raise StopRecovery("备份记录下载失败")

        raw = json.loads(cache_fp.read_text())
        os.remove(cache_fp)
        self.records = [BackupRecord(**i) for i in raw]

    def get_record(self, uuid: str) -> Optional[BackupRecord]:
        for record in self.records:
            if record.uuid == uuid:
                return record

    async def apply(self, record: BackupRecord) -> None:
        self.logger.info(f"正在恢复备份: {Style.CYAN(self.config.name)} - {Style.GREEN(record.timestr)}")
        self.logger.debug(f"备份记录: {Style.YELLOW(record)}")
        self.logger.info(f"备份uuid: [{Style.CYAN(record.uuid)}]")
        self.client = await self._backend.create()

        try:
            if self.config.mode == "compress":
                await self.apply_compress(record)
            elif self.config.mode == "increment":
                await self.apply_incremental(record)
        finally:
            shutil.rmtree(self.CACHE)

    def _finish_apply(self, uuid: str, result: Path) -> None:
        self.logger.info("备份下载完成，正在替换当前文件...")
        self.logger.debug(f"移动文件夹: {Style.PATH_DEBUG(result)} -> {Style.PATH_DEBUG(self.local)}")
        shutil.rmtree(self.local)
        mkdir(self.local.parent)
        shutil.move(result, self.local)
        self.logger.success(f"备份 [{Style.CYAN(uuid)}] 恢复完成!")

    # 模式: 压缩备份
    async def apply_compress(self, record: BackupRecord) -> None:
        cache = self.cache(record.uuid)
        cache_fp = cache / "backup.7z"
        result = mkdir(cache / "result")
        remote_fp = self.remote / record.uuid / "backup.7z"

        if not await self.client.get_file(cache_fp, remote_fp):
            raise StopRecovery(f"[{Style.CYAN(record.uuid)}] 备份文件下载失败")
        password = compress_password(record.uuid)
        await unpack_7zip(cache_fp, result, password)

        # 替换当前文件
        self._finish_apply(record.uuid, result)

    # 模式: 增量备份
    async def get_updates(self, records: List[BackupRecord]) -> Dict[str, Tuple[str, BackupUpdate]]:
        updates = {}
        for rec in records:
            self.logger.debug(f"加载备份 [{Style.CYAN(rec.uuid)}]")
            cache = self.cache(f"{rec.uuid}-{id(updates)}")

            # 下载备份清单
            cache_fp = cache / f"{rec.uuid}.json"
            remote_fp = self.remote / rec.uuid / "update.json"
            if not await self.client.get_file(cache_fp, remote_fp):
                raise StopRecovery(f"下载 [{Style.CYAN(rec.uuid)}] 备份清单失败")

            # 遍历备份清单
            for i in json.loads(cache_fp.read_text("utf-8")):
                upd = BackupUpdate(**i)
                updates[str(upd.path)] = (rec.uuid, upd)

            shutil.rmtree(cache)
            self.logger.debug(f"备份 [{Style.CYAN(rec.uuid)}] 加载完成")

        # 移除类型为del(删除)的记录
        for key, (_, upd) in list(updates.items()):
            if upd.type == "del":
                del updates[key]

        return updates

    async def apply_incremental(self, record: BackupRecord) -> None:
        records = [rec for rec in self.records if rec.timestamp <= record.timestamp]
        cache = self.cache(record.uuid)

        # 获取需要更新的文件清单
        updates = await self.get_updates(records)

        # 下载恢复备份需要的压缩包并解压
        multipart_cache = cache / "multipart.txt"
        archive_cache = cache / "archive"
        for uuid in {i[0] for i in updates.values()}:
            mkdir(archive_cache)
            remote = self.remote / uuid
            self.logger.debug(f"下载备份文件分卷清单: [{Style.CYAN(uuid)}]")
            if not await self.client.get_file(multipart_cache, remote / "multipart.txt"):
                raise StopRecovery(f"[{Style.CYAN(uuid)}] 备份文件分卷清单下载失败")
            archive_name = multipart_cache.read_text().splitlines()
            for name in archive_name:
                if not await self.client.get_file(archive_cache / name, remote / name):
                    raise StopRecovery(f"[{Style.CYAN(uuid)}] 备份文件 {Style.PATH(name)} 下载失败")
            password = compress_password(uuid)
            archive_head = archive_cache / archive_name[0]
            self.logger.debug(f"解压备份文件: [{Style.CYAN(uuid)}]")
            await unpack_7zip(archive_head, mkdir(cache / uuid), password)
            shutil.rmtree(archive_cache)

        # 从每个压缩包中提取需要的文件
        result = mkdir(cache / "result")
        for uuid, upd in updates.values():
            src = cache / uuid / upd.path
            dst = result / upd.path

            match upd.type:
                case "file":
                    mkdir(dst.parent)
                    if dst.exists():
                        os.remove(dst)
                    src.rename(dst)
                case "dir":
                    mkdir(dst)

        # 替换当前文件
        self._finish_apply(record.uuid, result)
