import asyncio
import time
from copy import deepcopy
from hashlib import md5
from pathlib import Path
from typing import Any, Dict, List, Literal, Self, Tuple, override

from aiohttp import ClientSession
from pydantic import BaseModel, Field

from src.const import VERSION, StrPath
from src.const.exceptions import BackendError, StopOperation
from src.utils import ByteReader, ByteWriter, Style, mkdir, run_sync

from ..backend import Backend, BackendResult
from ..config import parse_config
from .config import Config

config = parse_config(Config)
HEADERS = {
    "Accept": "application/json",
    "User-Agent": f"file-backup/{VERSION} wyf7685/7.6.8.5",
    "X-7685-Token": config.token,
}
MULTIPART_SIZE = 4 * 1024 * 1024


class Result(BaseModel):
    success: bool = Field()
    message: str = Field(default="")
    data: List[Any] = Field(default_factory=list)

    @property
    def failed(self):
        return not self.success


def solve_params(key: str, *data: Any) -> bytes:
    writer = ByteWriter(key)
    for value in data:
        if isinstance(value, Path):
            writer.write(value.as_posix())
        elif isinstance(value, (bytes, bool, int, float)):
            writer.write(value)
        elif isinstance(value,memoryview):
            writer.write(bytes(value))
        elif isinstance(value, list):
            writer.write(value)  # type: ignore
        else:
            writer.write(str(value))
    return writer.get()


class ServerBackend(Backend):
    session: ClientSession

    @override
    @classmethod
    async def create(cls) -> Self:
        self = cls()
        self.session = ClientSession()

        if not config.url.endswith("/"):
            config.url += "/"
        res = await self._request("status")
        if res.failed:
            raise StopOperation(f"ServerBackend 状态异常: {res.message!r}")
        return self

    def _get_headers(self) -> Dict[str, str]:
        salt = str(time.time())
        hash_val = config.api_key + salt
        hash_val = md5(hash_val.encode("utf-8")).hexdigest()
        headers = deepcopy(HEADERS)
        headers["X-7685-Salt"] = salt
        headers["X-7685-Hash"] = hash_val
        return headers

    async def _request(self, api: str, *params: Any) -> Result:
        url = f"{config.url}api/{api}"
        data = solve_params(config.api_key, *params)
        headers = self._get_headers()

        try:
            async with self.session.post(url, data=data, headers=headers) as resp:
                result = ByteReader(await resp.read(), config.api_key)
        except Exception as e:
            return Result(success=False, message=f"{e.__class__.__name__}: {e}")

        if not result.read_bool():
            return Result(success=False, message=result.read_string())
        received: List[Any] = []
        while result.any():
            received.append(result.read())
        return Result(success=True, data=received)

    @override
    async def _mkdir(self, path: StrPath) -> None:
        res = await self._request("mkdir", path)
        if res.failed:
            self.logger.error(res.message)
            raise BackendError(f"创建文件夹时出错: {res.message}")

    @override
    async def _rmdir(self, path: StrPath) -> None:
        res = await self._request("rmdir", path)
        if res.failed:
            self.logger.error(res.message)
            raise BackendError(f"删除文件夹时出错: {res.message}")

    @override
    async def _list_dir(
        self, path: StrPath = "."
    ) -> Tuple[BackendResult, List[Tuple[Literal["d", "f"], str]]]:
        res = await self._request("list_dir", path)
        if res.failed:
            self.logger.error(res.message)
            return BackendError(f"列出文件夹时出错: {res.message}"), []
        return None, sorted(res.data[0])

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
                await self.__get_multipart(local_fp, remote_fp)
                return
            except BackendError as e:
                err = e.msg
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
                await self.__put_multipart(local_fp, remote_fp)
                return
            except BackendError as e:
                err = e.msg
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

    async def __get_prepare(self, remote_fp: Path) -> Tuple[str, int]:
        result = await self._request("get_file/prepare", remote_fp)
        if result.failed:
            raise BackendError(result.message)
        return result.data[0], result.data[1]

    async def __get_getpart(self, uuid: str, seq: int) -> bytes:
        result = await self._request("get_file/getpart", uuid, seq)
        if result.failed:
            raise BackendError(result.message)
        return result.data[0]

    async def __get_multipart(self, local_fp: Path, remote_fp: Path) -> None:
        uuid, seqs = await self.__get_prepare(remote_fp)
        with local_fp.open("wb") as file:
            write = run_sync(file.write)
            for seq in range(seqs):
                block = await self.__get_getpart(uuid, seq)
                await write(block)

    async def __put_prepare(self, block_md5: List[str], remote_fp: Path) -> str:
        result = await self._request("put_file/prepare", block_md5, remote_fp)
        if result.failed:
            raise BackendError(result.message)
        return result.data[0]

    async def __put_putpart(self, uuid: str, seq: int, part: memoryview):
        result = await self._request("put_file/putpart", uuid, seq, part)
        if result.failed:
            raise BackendError(result.message)

    async def __put_finish(self, uuid: str):
        result = await self._request("put_file/finish", uuid)
        if result.failed:
            raise BackendError(result.message)

    async def __put_multipart(self, local_fp: Path, remote_fp: Path):
        data = await run_sync(local_fp.read_bytes)()
        blocks: List[memoryview] = []
        idx = 0
        while idx < len(data):
            blocks.append(memoryview(data[idx : idx + MULTIPART_SIZE]).toreadonly())
            idx += MULTIPART_SIZE

        uuid = await self.__put_prepare(
            [md5(i).hexdigest() for i in blocks],
            remote_fp,
        )

        for seq, block in enumerate(blocks):
            await self.__put_putpart(uuid, seq, block)

        await self.__put_finish(uuid)
