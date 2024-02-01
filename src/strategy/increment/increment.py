import asyncio
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, override

from src.const import BackupUpdateType
from src.const.exceptions import StopBackup, StopRecovery
from src.models import BackupRecord, BackupUpdate
from src.utils import (
    Style,
    compress_password,
    get_md5,
    get_uuid,
    json,
    mkdir,
    pack_7zip_multipart,
    run_sync,
    unpack_7zip,
)

from ..strategy import Strategy


class IncrementStrategy(Strategy):
    __strategy_name__: str = "Increment"

    def get_local_list(self) -> List[Tuple[BackupUpdateType, Path]]:
        """获取本地文件列表

        Returns:
            `List[Tuple[BackupUpdateType, Path]]`: 列表元素为元组: ("file"或"dir", 相对路径)
        """
        res: List[Tuple[BackupUpdateType, Path]] = []

        for p, dirs, files in self.local.walk():
            relp = p.relative_to(self.local)
            res.extend(("dir", relp / i) for i in dirs)
            res.extend(("file", relp / i) for i in files)

        return sorted(res)

    async def get_local_md5(self, fp_list: List[Path]) -> Dict[Path, str]:
        call = run_sync(get_md5)

        async def _run(p: Path) -> Tuple[Path, str]:
            return p, await call(self.local / p)

        return dict(await asyncio.gather(*[_run(p) for p in fp_list]))

    async def get_update_list(self) -> List[BackupUpdate]:
        remote: Dict[Path, BackupUpdate] = {}

        # 按序遍历历史备份
        for rec in self.record:
            name = f"{Style.CYAN(self.config.name)} [{Style.CYAN(rec.uuid)}]"
            self.logger.debug(f"下载 {name} 的备份清单")
            cache_fp = self.CACHE / f"{rec.uuid}.json"
            remote_fp = self.remote / rec.uuid / "update.json"

            # 下载备份修改记录
            if err := await self.client.get_file(cache_fp, remote_fp):
                raise StopBackup(f"下载备份清单 {remote_fp} 失败") from err

            # 读取备份修改记录
            for i in json.loads(cache_fp.read_text("utf-8")):
                upd = BackupUpdate.model_validate(i)
                if upd.md5 != "":
                    remote[upd.path] = upd
                elif upd.path in remote and remote[upd.path].type == "del":
                    del remote[upd.path]

        # 获取本地文件列表
        local_list = self.get_local_list()

        # 计算文件md5值
        md5_cache = await self.get_local_md5([p for t, p in local_list if t == "file"])

        # 对比本地待备份文件
        res: List[Tuple[BackupUpdateType, Path]] = []
        for t, p in local_list:
            if t == "dir":
                if p not in remote:
                    res.append((t, p))
            elif t == "file":
                if p not in remote or remote[p].md5 != md5_cache[p]:
                    res.append((t, p))
            if p in remote:
                del remote[p]

        res.extend(("del", v.path) for v in remote.values())
        return [
            BackupUpdate(
                type=t,
                path=p,
                md5=md5_cache.get(p, None),
            )
            for t, p in res
        ]

    def cache_update(self, update: List[BackupUpdate]) -> Path:
        cache = self.cache(get_uuid())

        for upd in update:
            if upd.type == "dir":
                mkdir(cache / upd.path)
            elif upd.type == "file":
                mkdir(cache / upd.path.parent)
                shutil.copyfile(self.local / upd.path, cache / upd.path)

        return cache

    async def compress_and_upload(self, uuid: str, cache: Path):
        target = self.remote / uuid
        await self.client.mkdir(target)
        password = compress_password(uuid)
        archive_dir = self.cache("archive")

        self.logger.debug("开始压缩待备份文件...")
        archives = await pack_7zip_multipart(
            archive_dir / f"{uuid}.7z",
            cache,
            volume_size=100,
            password=password,
        )
        self.logger.debug("待备份文件分卷压缩完成")

        self.logger.debug(f"本地备份文件分卷压缩包目录: {Style.PATH_DEBUG(archive_dir)}")
        self.logger.info(f"[{Style.CYAN(uuid)}] 正在上传...")

        async def upload(archive: Path) -> None:
            if err := await self.client.put_file(archive, target / archive.name):
                raise StopBackup(f"上传分卷压缩包 {Style.PATH(archive.name)} 失败") from err

        await asyncio.gather(*[upload(i) for i in archives])

        multipart_cache = cache / "multipart.txt"
        multipart_cache.write_text("\n".join(i.name for i in archives))
        self.logger.debug(f"上传分卷清单: {Style.PATH_DEBUG(multipart_cache)}")
        if err := await self.client.put_file(
            multipart_cache, target / multipart_cache.name
        ):
            raise StopBackup("上传分卷清单失败") from err

    @override
    async def _make_backup(self) -> None:
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
        self.logger.info(f"开始增量备份: {Style.PATH(self.local)}")
        self.logger.info(f"备份uuid: [{Style.CYAN(uuid)}]")

        # 复制文件到缓存目录
        cache = self.cache_update(update)

        # 压缩文件并上传
        await self.compress_and_upload(uuid, cache)

        # 生成本次备份清单
        upd_file_cnt = len([upd for upd in update if upd.type == "file"])
        upd_cache = cache / "update.json"
        upd_cache.write_text(json.dumps([upd.model_dump() for upd in update]))
        if err := await self.client.put_file(upd_cache, target / "update.json"):
            raise StopBackup(f"上传备份清单时出现错误: {err}") from err

        # 更新备份记录
        await self.add_record(uuid)
        self.logger.success(f"[{Style.CYAN(uuid)}] 备份完成!")
        self.logger.success(f"本次备份更新 {Style.YELLOW(upd_file_cnt)} 个文件")

    async def get_updates(
        self, records: List[BackupRecord]
    ) -> Dict[Path, Tuple[str, BackupUpdate]]:
        updates: Dict[Path, Tuple[str, BackupUpdate]] = {}
        cache_prefix = f"{id(updates)}-"
        for rec in records:
            self.logger.debug(f"加载备份 [{Style.CYAN(rec.uuid)}]")
            cache = self.cache(cache_prefix + rec.uuid)

            # 下载备份清单
            cache_fp = cache / f"{rec.uuid}.json"
            remote_fp = self.remote / rec.uuid / "update.json"
            if err := await self.client.get_file(cache_fp, remote_fp):
                raise StopRecovery(f"下载 [{Style.CYAN(rec.uuid)}] 备份清单失败") from err

            # 遍历备份清单
            for i in json.loads(cache_fp.read_text("utf-8")):
                upd = BackupUpdate.model_validate(i)
                updates[upd.path] = (rec.uuid, upd)

            shutil.rmtree(cache)
            self.logger.debug(f"备份 [{Style.CYAN(rec.uuid)}] 加载完成")

        # 移除类型为del(删除)的记录
        return {
            key: (uuid, upd)
            for key, (uuid, upd) in updates.items()
            if upd.type != "del"
        }

    @override
    async def _make_recovery(self, record: BackupRecord) -> Path:
        records = [rec for rec in self.record if rec.timestamp <= record.timestamp]
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
            if err := await self.client.get_file(
                multipart_cache, remote / "multipart.txt"
            ):
                raise StopRecovery(f"[{Style.CYAN(uuid)}] 备份文件分卷清单下载失败") from err
            archive_name = multipart_cache.read_text().splitlines()
            for name in archive_name:
                if err := await self.client.get_file(
                    archive_cache / name, remote / name
                ):
                    raise StopRecovery(
                        f"[{Style.CYAN(uuid)}] 备份文件 {Style.PATH(name)} 下载失败"
                    ) from err
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
                        dst.unlink(True)
                    src.rename(dst)
                case "dir":
                    mkdir(dst)
                case _:
                    pass

        return result
