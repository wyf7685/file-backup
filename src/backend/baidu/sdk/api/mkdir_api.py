from pathlib import Path
from typing import Any, Dict

from src.utils import Style, run_sync

from ..const import PATH_ROOT
from ..exceptions import BaiduMakeDirectoryError
from ..openapi_client import ApiClient, ApiException
from ..openapi_client.api.fileupload_api import FileuploadApi
from ..sdk_config import config, get_logger


async def create(
    path: str,
) -> Dict[str, Any]:
    with ApiClient() as client:
        return await run_sync(
            lambda: FileuploadApi(client).xpanfilecreate(
                access_token=config.access_token,
                path=path,
                isdir=0,
                size=0,
                uploadid="",
                block_list="[]",
                rtype=3,
            )
        )()


async def mkdir(path: Path):
    logger = get_logger("mkdir").opt(colors=True)
    logger.debug(f"创建目录: {Style.PATH_DEBUG(path)}")
    try:
        resp = await create((PATH_ROOT / path).as_posix())
    except ApiException as err:
        raise BaiduMakeDirectoryError(
            f"创建目录 {Style.PATH(path)} 时遇到错误:\n{Style.RED(err)}"
        ) from err

    if resp["errno"] not in {0, 10}:
        raise BaiduMakeDirectoryError(
            f"创建目录 {Style.PATH(path)} 失败, 错误码: {Style.RED(resp['errno'])}"
        )
