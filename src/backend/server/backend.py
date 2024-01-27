import asyncio
import time
from base64 import b64decode, b64encode
from copy import deepcopy
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List, Literal, Self, Tuple, cast, override

from aiohttp import ClientSession
from pydantic import BaseModel, Field

from src.const import VERSION, StrPath
from src.const.exceptions import BackendError, StopOperation
from src.utils import Style, mkdir, run_sync

from ..backend import Backend, BackendResult
from .config import Config

HEADERS = {
    "Accept": "application/json",
    "User-Agent": f"file-backup/{VERSION} wyf7685/7.6.8.5",
}


class _Result(BaseModel):
    status: Literal["success", "error"] = Field()
    message: str = Field(default="")
    data: Dict[str, Any] = Field(default_factory=dict)

    @property
    def success(self):
        return self.status == "success"

    @property
    def failed(self):
        return not self.success


class ServerBackend(Backend):
    config: Config
    session: ClientSession
    headers: Dict[str, str]

    @override
    @classmethod
    async def create(cls) -> Self:
        self = cls()
        self.config = self._parse_config(Config)
        self.headers = deepcopy(HEADERS)
        self.headers["X-7685-Token"] = self.config.token
        self.session = ClientSession()

        if not self.config.url.endswith("/"):
            self.config.url += "/"
        res = await self._request("status")
        if res.failed:
            raise StopOperation(f"ServerBackend 状态异常: {res.message}")
        return self

    async def _request(self, api: str, **data) -> _Result:
        url = f"{self.config.url}api/{api}"
        for k in data:
            if isinstance(data[k], Path):
                data[k] = cast(Path, data[k]).as_posix()

        salt = str(time.time())
        hash_val = self.config.api_key + salt
        hash_val = md5(hash_val.encode("utf-8")).hexdigest()
        headers = deepcopy(self.headers)
        headers["X-7685-Salt"] = salt
        headers["X-7685-Hash"] = hash_val

        try:
            async with self.session.post(url, json=data, headers=headers) as resp:
                return _Result.model_validate(await resp.json())
        except Exception as e:
            return _Result(status="error", message=f"{e.__class__.__name__}: {e}")

    @override
    async def _mkdir(self, path: StrPath) -> None:
        res = await self._request("mkdir", path=path)
        if res.failed:
            self.logger.error(res.message)
            raise BackendError(f"创建文件夹时出错: {res.message}")

    @override
    async def _rmdir(self, path: StrPath) -> None:
        res = await self._request("rmdir", path=path)
        if res.failed:
            self.logger.error(res.message)
            raise BackendError(f"删除文件夹时出错: {res.message}")

    @override
    async def _list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        res = await self._request("list_dir", path=path)
        if res.failed:
            self.logger.error(res.message)
            return BackendError(f"列出文件夹时出错: {res.message}"), []
        return None, sorted(res.data["list"])

    @override
    async def _get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        err = None
        for _ in range(max_try):
            try:
                res = await self._request("get_file", path=remote_fp)
                if res.success:
                    data = b64decode(res.data["file"])
                    with local_fp.open("wb") as f:
                        await run_sync(f.write)(data)
                    return
                err = res.message
                break
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
        if not local_fp.is_file():
            msg = f"上传文件失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            return BackendError(msg)

        await self.mkdir(remote_fp.parent)

        err = None
        for _ in range(max_try):
            try:
                with local_fp.open("rb+") as f:
                    data = await run_sync(f.read)()
                res = await self._request(
                    "put_file",
                    path=remote_fp,
                    file=b64encode(data).decode("utf-8"),
                )
                if res.success:
                    return
                err = res.message
                break
            except Exception as e:
                err = e
        msg = f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {Style.RED(err)}"
        self.logger.debug(msg)
        return BackendError(msg)

    @override
    async def _get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)

        err, res = await self.list_dir(remote_fp)
        if err:
            return err

        for t, name in res:
            local = local_fp / name
            remote = remote_fp / name
            if t == "d":
                if err := await self.get_tree(mkdir(local), remote, max_try):
                    return err
            elif t == "f":
                if err := await self.get_file(local, remote, max_try):
                    return err

    @override
    async def _put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> BackendResult:
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if not local_fp.exists() or not local_fp.is_dir():
            msg = f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在"
            self.logger.debug(msg)
            return BackendError(msg)

        for p in local_fp.iterdir():
            if p.is_dir():
                await self.mkdir(remote_fp / p.name)
                if err := await self.put_tree(p, remote_fp / p.name, max_try):
                    return err
            elif p.is_file():
                if err := await self.put_file(p, remote_fp / p.name, max_try):
                    return err

    def __del__(self):
        asyncio.create_task(self.session.close())
