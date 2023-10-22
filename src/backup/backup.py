import asyncio
import json
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type

from src.backend import Backend, get_backend
from src.const import PATH
from src.const.exceptions import RestartBackup, StopBackup
from src.log import get_logger
from src.models import *
from src.utils import (
    Style,
    compress_password,
    get_md5,
    get_uuid,
    mkdir,
    pack_7zip,
    pack_7zip_multipart,
    notify,
    run_sync,
)

if TYPE_CHECKING:
    from src.log import Logger


class Backup(object):
    config: BackupConfig
    logger: "Logger"
    client: Backend
    record: List[BackupRecord]
    _backend: Type[Backend]
    _cache: Path

    def __init__(self, backup_config: BackupConfig, silent: bool = False) -> None:
        self.config = backup_config
        self._backend = get_backend()
        self._cache = PATH.CACHE / "backup" / get_uuid().split("-")[0]
        name = self.config.name
        self.logger = get_logger(name).opt(colors=True)
        if not silent:
            self.logger.success(f"{Style.GREEN('backup')} [{Style.CYAN(name)}] 初始化成功")

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

    async def apply(self):
        while True:
            try:
                await self.prepare()
                await self.make_backup()
                self.logger.success("备份完成")
            except StopBackup as e:
                # 中止备份
                self.logger.warning(f"备份错误: {e}")
                if e.uuid:
                    await self.client.rmdir(self.remote / e.uuid)
            except RestartBackup as e:
                # 重启备份
                self.logger.warning(f"重启备份: {e}")
                continue
            except Exception as e:
                self.logger.opt(exception=True).exception(f"未知错误: {e}")
                self.logger.warning("重启备份...")
                continue
            finally:
                del self.client
                shutil.rmtree(self.CACHE, True)
                return

    async def load_record(self) -> None:
        remote_fp = self.remote / "backup.json"
        cache_fp = self.CACHE / "backup.json"

        # 下载备份记录
        if not await self.client.get_file(cache_fp, remote_fp):
            self.logger.info("备份记录不存在, 正在创建...")
            cache_fp.write_text("[]")

        raw = cache_fp.read_text()
        os.remove(cache_fp)
        self.record = [BackupRecord.parse_obj(i) for i in json.loads(raw)]

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
                [json.loads(record.json()) for record in self.record],
                indent=4,
            ),
            encoding="utf-8",
        )

        # 上传备份清单
        if not await self.client.put_file(cache_fp, remote_fp):
            raise StopBackup("上传备份记录失败")
        os.remove(cache_fp)

    def check_local(self) -> None:
        # 本地待备份路径错误
        if not self.local.exists():
            raise StopBackup(f"目标路径 {Style.PATH(self.local)} 不存在")

        if self.config.mode == "increment" and self.local.is_file():
            raise StopBackup("increment模式的路径不能是单个文件, 请使用compress模式")

    def check_uuid(self, uuid: str) -> None:
        if [i for i in self.record if i.uuid == uuid]:
            raise RestartBackup("uuid重复")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name})"

    async def _notify_before_backup(self, time: datetime) -> None:
        timestr = time.strftime("%Y-%m-%d %H:%M:%S")

        title = f"开始备份: {self.config.name}"
        body = [
            f"备份路径: {self.config.local_path}",
            f"当前时间: {timestr}",
            f"备份模式: {self.config.mode}",
        ]
        await notify(title, "\n".join(body))

    async def _notify_after_backup(self, start_time: datetime) -> None:
        now = datetime.now()
        delta = now - start_time
        next_time = now + timedelta(seconds=self.config.interval)
        timestr = next_time.strftime("%Y-%m-%d %H:%M:%S")

        title = f"备份完成: {self.config.name}"
        body = [
            f"备份耗时: {delta.total_seconds()}s",
            f"备份路径: {self.config.local_path}",
            f"预计下次备份: {timestr}",
        ]
        await notify(title, "\n".join(body))

    async def prepare(self) -> None:
        self.client = self._backend()
        await self.client.mkdir(str(self.remote))
        await self.load_record()

    async def make_backup(self) -> None:
        start = datetime.now()
        await self._notify_before_backup(start)

        if self.config.mode == "compress":
            await self.make_compress()
        elif self.config.mode == "increment":
            await self.make_incremental()

        await self._notify_after_backup(start)

    # 模式: 压缩备份
    async def make_compress(self) -> None:
        self.check_local()
        uuid = get_uuid()
        self.check_uuid(uuid)

        # 准备备份
        target = self.remote / uuid
        await self.client.mkdir(target)
        self.logger.info(f"开始压缩备份: {Style.PATH(self.local)}")
        self.logger.info(f"备份uuid: [{Style.CYAN(uuid)}]")

        # 压缩后上传
        password = compress_password(uuid)
        archive = await pack_7zip(self.cache(f"{uuid}.7z"), self.local, password)
        self.logger.info(f"[{Style.CYAN(uuid)}] 正在上传...")
        await self.client.put_file(archive, target / "backup.7z")

        # 更新备份记录
        await self.add_record(uuid)
        self.logger.success(f"[{Style.CYAN(uuid)}] 备份完成!")

    # 模式: 增量备份
    def get_local_list(self) -> List[Tuple[BackupUpdateType, Path]]:
        """获取本地文件列表

        Returns:
            List[Tuple[str, Path]]: 列表元素为元组: ("file"或"dir", 相对路径)
        """
        res = []

        def iter_dir(dir: Path, r: Path) -> None:
            # self.logger.debug(f"遍历目录: {Style.PATH_DEBUG(dir)}")
            for p in dir.iterdir():
                if p.is_file():
                    res.append(("file", r / p.name))
                elif p.is_dir():
                    res.append(("dir", r / p.name))
                    iter_dir(p, r / p.name)

        iter_dir(self.local, Path())

        res.sort(key=lambda x: x[0])
        return res
    
    async def get_local_md5(self, fp_list: List[Path]) -> Dict[str, str]:
        call = run_sync(get_md5)
        async def _run(p: Path) -> Tuple[str, str]:
            return str(p), await call(self.local/p)
        data = await asyncio.gather(*[_run(p) for p in fp_list])
        return dict(data)

    async def get_update_list(self) -> List[BackupUpdate]:
        remote = {}  # type: Dict[str, BackupUpdate]
        res = []  # type: List[Tuple[BackupUpdateType, Path]]
        local_list = self.get_local_list()

        # 按序遍历历史备份
        for uuid in [i.uuid for i in self.record]:
            self.logger.debug(f"下载 [{Style.CYAN(uuid)}] 的备份清单")
            cache_fp = self.CACHE / f"{uuid}.json"
            remote_fp = self.remote / uuid / "update.json"

            # 下载备份修改记录
            if not await self.client.get_file(cache_fp, remote_fp):
                raise StopBackup(f"下载备份清单 {remote_fp} 失败")

            # 将修改记录转换为对象
            remote_upd = [
                BackupUpdate.parse_obj(i)
                for i in json.loads(cache_fp.read_text("utf-8"))
            ]

            # 读取备份修改记录
            for upd in remote_upd:
                key = str(upd.path)
                if upd.md5 != "":
                    remote[key] = upd
                elif key in remote and remote[key].type == "del":
                    del remote[key]

        # 计算文件md5值
        md5_cache = await self.get_local_md5([p for t, p in local_list if t == "file"])

        # 对比本地待备份文件
        for t, p in local_list:
            key = str(p)
            if t == "dir":
                if key not in remote:
                    res.append((t, p))
            elif t == "file":
                # md5_cache[key] = get_md5(self.local / p)
                if key not in remote or (
                    key in remote and not remote[key].check(md5_cache[key])
                ):
                    res.append((t, p))
            if key in remote:
                del remote[key]

        res.extend(("del", v.path) for v in remote.values())

        return [BackupUpdate(type=t, path=p, md5=md5_cache.get(str(p))) for t, p in res]

    def cache_update(self, update: List[BackupUpdate]) -> Path:
        cache = self.cache(get_uuid())

        for upd in update:
            if upd.type == "dir":
                mkdir(cache / upd.path)
            elif upd.type == "file":
                mkdir(cache / upd.path.parent)
                shutil.copyfile(self.local / upd.path, cache / upd.path)

        return cache

    async def compress_and_upload(self, uuid: str, cache: Path, target: Path):
        target = self.remote / uuid
        password = compress_password(uuid)
        archive_dir = self.cache("archive")

        self.logger.debug("开始压缩待备份文件...")
        archives = await pack_7zip_multipart(
            archive_dir / f"{uuid}.7z", cache, volume_size=100, password=password
        )
        self.logger.debug("待备份文件分卷压缩完成")

        self.logger.debug(f"本地备份文件分卷压缩包目录: {Style.PATH_DEBUG(archive_dir)}")
        self.logger.info(f"[{Style.CYAN(uuid)}] 正在上传...")
        async def upload(archive: Path) -> None:
            if not await self.client.put_file(archive, target / archive.name):
                raise StopBackup(f"上传分卷压缩包 {Style.PATH(archive.name)} 失败")
        await asyncio.gather(*[upload(i) for i in archives])
        
        multipart_cache = cache / "multipart.txt"
        multipart_cache.write_text("\n".join(i.name for i in archives))
        self.logger.debug(f"上传分卷清单: {Style.PATH_DEBUG(multipart_cache)}")
        if not await self.client.put_file(
            multipart_cache, target / multipart_cache.name
        ):
            raise StopBackup("上传分卷清单失败")

    async def make_incremental(self) -> None:
        """执行一次增量备份"""
        self.check_local()
        uuid = get_uuid()
        self.check_uuid(uuid)

        # 获取本次需要备份的文件
        self.logger.info("正在比对本地待备份文件...")
        update = await self.get_update_list()
        if not update:
            self.logger.info("本次备份未更新文件...跳过备份")
            return

        # 准备备份
        target = self.remote / uuid
        await self.client.mkdir(target)
        self.logger.info(f"开始增量备份: {Style.PATH(self.local)}")
        self.logger.info(f"备份uuid: [{Style.CYAN(uuid)}]")

        # 复制文件到缓存目录
        cache = self.cache_update(update)

        # 压缩文件并上传
        await self.compress_and_upload(uuid, cache, target)

        # 生成本次备份清单
        upd_file_cnt = len([upd for upd in update if upd.type == "file"])
        upd_cache = cache / "update.json"
        upd_cache.write_text(json.dumps([json.loads(upd.json()) for upd in update]))
        await self.client.put_file(upd_cache, target / "update.json")

        # 更新备份记录
        await self.add_record(uuid)
        self.logger.success(f"[{Style.CYAN(uuid)}] 备份完成!")
        self.logger.success(f"本次备份更新 {Style.YELLOW(upd_file_cnt)} 个文件")
