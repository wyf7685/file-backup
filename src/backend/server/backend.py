import asyncio
import time
from base64 import b64decode, b64encode
from copy import deepcopy
from hashlib import md5
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Self,
    Tuple,
    TypeAlias,
    override,
)

from aiohttp import ClientSession
from pydantic import BaseModel, Field

from src.const import *
from src.const.exceptions import StopOperation
from src.models import ServerConfig
from src.utils import Style, mkdir, run_sync

from ..backend import Backend

if TYPE_CHECKING:
    from src.log import Logger

HEADERS = {
    "Accept": "application/json",
    "User-Agent": f"file-backup/{VERSION} wyf7685/7.6.8.5",
}


_ResultStatus: TypeAlias = Literal["success", "error"]


class _Result(BaseModel):
    status: _ResultStatus = Field()
    message: str = Field(default="")
    data: Dict[str, Any] = Field(default_factory=dict)

    @property
    def success(self):
        return self.status == "success"

    @property
    def failed(self):
        return not self.success


class ServerBackend(Backend):
    logger: "Logger"
    config: ServerConfig
    session: ClientSession
    headers: Dict[str, str]

    @override
    def __init__(self) -> None:
        from src.models import config

        super(ServerBackend, self).__init__()

        self.config = config.backend.server
        self.headers = deepcopy(HEADERS)
        self.headers["X-7685-Token"] = self.config.token
        self.session = ClientSession()

        if not self.config.url.endswith("/"):
            self.config.url += "/"

    @override
    @classmethod
    async def create(cls) -> Self:
        self = await super().create()
        res = await self._request("status")
        if res.failed:
            raise StopOperation(f"ServerBackend 状态异常: {res.message}")
        return self

    async def _request(self, api: str, **data) -> _Result:
        url = f"{self.config.url}api/{api}"
        for k in data:
            if isinstance(data[k], Path):
                data[k] = str(data[k]).replace("\\", "/")

        salt = str(time.time())
        hash = self.config.api_key + salt
        hash = md5(hash.encode("utf-8")).hexdigest()
        headers = deepcopy(self.headers)
        headers["X-7685-Salt"] = salt
        headers["X-7685-Hash"] = hash

        try:
            async with self.session.post(url, json=data, headers=headers) as resp:
                return _Result.model_validate(await resp.json())
        except Exception as e:
            return _Result(status="error", message=f"{e.__class__.__name__}: {e}")

    @override
    async def mkdir(self, path: StrPath) -> None:
        await super(ServerBackend, self).mkdir(path)
        res = await self._request("mkdir", path=path)
        if res.failed:
            self.logger.error(res.message)

    @override
    async def rmdir(self, path: StrPath) -> None:
        await super(ServerBackend, self).rmdir(path)
        res = await self._request("rmdir", path=path)
        if res.failed:
            self.logger.error(res.message)

    @override
    async def list_dir(self, path: StrPath = ".") -> List[Tuple[str, str]]:
        await super(ServerBackend, self).list_dir(path)
        res = await self._request("list_dir", path=path)
        if res.failed:
            self.logger.error(res.message)
            return []
        return sorted(res.data["list"])

    @override
    async def get_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(ServerBackend, self).get_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)

        err = None
        for _ in range(max_try):
            try:
                res = await self._request("get_file", path=remote_fp)
                if res.success:
                    with local_fp.open("wb") as f:
                        await run_sync(f.write)(b64decode(res.data["file"]))
                    return True
                err = res.message
                break
            except Exception as e:
                err = e
        self.logger.debug(f"下载文件 {Style.PATH_DEBUG(remote_fp)} 时出现异常: {Style.RED(err)}")
        return False

    @override
    async def put_file(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(ServerBackend, self).put_file(local_fp, remote_fp, max_try)

        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if not local_fp.is_file():
            self.logger.debug(f"上传文件失败: {Style.PATH_DEBUG(local_fp)} 不存在")
            return False

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
                    return True
                err = res.message
                break
            except Exception as e:
                err = e
        self.logger.debug(f"上传文件 {Style.PATH_DEBUG(local_fp)} 时出现异常: {Style.RED(err)}")
        return False

    @override
    async def get_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(ServerBackend, self).get_tree(local_fp, remote_fp, max_try)

        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)

        for t, name in await self.list_dir(remote_fp):
            local = local_fp / name
            remote = remote_fp / name
            if t == "d":
                if not await self.get_tree(mkdir(local), remote, max_try):
                    return False
            elif t == "f":
                if not await self.get_file(local, remote, max_try):
                    return False

        return True

    @override
    async def put_tree(
        self, local_fp: StrPath, remote_fp: StrPath, max_try: int = 3
    ) -> bool:
        await super(ServerBackend, self).put_tree(local_fp, remote_fp, max_try)

        if isinstance(remote_fp, str):
            remote_fp = Path(remote_fp)
        if isinstance(local_fp, str):
            local_fp = Path(local_fp)
        if not local_fp.exists() or not local_fp.is_dir():
            self.logger.debug(f"上传目录失败: {Style.PATH_DEBUG(local_fp)} 不存在")
            return False

        for p in local_fp.iterdir():
            if p.is_dir():
                await self.mkdir(remote_fp / p.name)
                if not await self.put_tree(p, remote_fp / p.name, max_try):
                    return False
            elif p.is_file():
                if not await self.put_file(p, remote_fp / p.name, max_try):
                    return False

        return True

    def __del__(self):
        asyncio.create_task(self.session.close())
