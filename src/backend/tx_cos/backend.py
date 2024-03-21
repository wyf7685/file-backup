from pathlib import Path
from typing import List, Literal, Tuple, final, override

from src.const.exceptions import BackendError
from src.utils import Style, run_sync

from ..backend import Backend, BackendResult
from ..config import parse_config
from .config import Config
from .sdk import init_client, get_file, put_file, list_dir, rm_dir

config = parse_config(Config)
init_client(
    config.secret_id,
    config.secret_key,
    config.region,
    config.bucket,
)


@final
class TencentCOSBackend(Backend):
    @override
    async def _mkdir(self, path: Path) -> None:
        # 腾讯云 COS 不需要创建文件夹
        return

    @override
    async def _rmdir(self, path: Path) -> None:
        await run_sync(rm_dir)(path.as_posix())

    @override
    async def _list_dir(
        self, path: Path = Path()
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        try:
            return None, await run_sync(list_dir)(path.as_posix())
        except Exception as e:
            msg = f"列出文件夹时出现错误: {e.__class__.__name__} - {e}"
            return BackendError(msg), []

    @override
    async def _get_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult:
        try:
            await run_sync(get_file)(local_fp, remote_fp, max_try)
        except Exception as e:
            msg = f"下载文件 {Style.PATH(remote_fp)} 时出现错误: {e.__class__.__name__} - {e}"
            return BackendError(msg)

    @override
    async def _put_file(
        self, local_fp: Path, remote_fp: Path, max_try: int = 3
    ) -> BackendResult:
        try:
            await run_sync(put_file)(local_fp, remote_fp, max_try)
        except Exception as e:
            msg = f"上传文件 {Style.PATH(local_fp)} 时出现错误: {e.__class__.__name__} - {e}"
            return BackendError(msg)
