from pathlib import Path
from typing import override

from src.const.exceptions import StopRecovery, StopBackup
from src.models import BackupRecord
from src.utils import Style, compress_password, get_uuid, mkdir, pack_7zip, unpack_7zip

from ..strategy import Strategy


class CompressStrategy(Strategy):
    __strategy_name__: str = "Compress"

    @override
    async def _make_backup(self) -> None:
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
        if err := await self.client.put_file(archive, target / "backup.7z"):
            raise StopBackup(f"上传备份压缩包时出错: {err}") from err

        # 更新备份记录
        await self.add_record(uuid)
        self.logger.success(f"[{Style.CYAN(uuid)}] 备份完成!")

    @override
    async def _make_recovery(self, record: BackupRecord) -> Path:
        cache = self.cache(record.uuid)
        cache_fp = cache / "backup.7z"
        result = mkdir(cache / "result")
        remote_fp = self.remote / record.uuid / "backup.7z"

        if err := await self.client.get_file(cache_fp, remote_fp):
            raise StopRecovery(f"[{Style.CYAN(record.uuid)}] 备份文件下载失败") from err
        password = compress_password(record.uuid)
        await unpack_7zip(cache_fp, result, password)
        return result
