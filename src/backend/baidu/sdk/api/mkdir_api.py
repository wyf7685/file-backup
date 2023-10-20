from pathlib import Path
from typing import Any, Dict

from src.log import get_logger
from src.utils import Style, run_sync

from .. import openapi_client
from ..const import *
from ..exceptions import BaiduMakeDirectoryError
from ..openapi_client.api import fileupload_api
from ..sdk_config import config


async def create(
    path: str,
) -> Dict[str, Any]:
    with openapi_client.ApiClient() as client:
        api = fileupload_api.FileuploadApi(client)
        call = lambda: api.xpanfilecreate(
            access_token=config.access_token,
            path=path,
            isdir=0,
            size=0,
            uploadid="",
            block_list="[]",
            rtype=3,
        )
        resp = await run_sync(call)()
    return resp


async def mkdir(path: Path):
    logger = get_logger("Baidu:mkdir").opt(colors=True)
    logger.debug(f"创建目录: {Style.PATH_DEBUG(path)}")
    try:
        resp = await create(str(PATH_ROOT / path).replace("\\", "/"))
    except openapi_client.ApiException as err:
        raise BaiduMakeDirectoryError(
            f"创建目录 {Style.PATH(path)} 时遇到错误:\n{Style.RED(err)}"
        ) from err

    if resp["errno"] not in {0, 10}:
        raise BaiduMakeDirectoryError(
            f"创建目录 {Style.PATH(path)} 失败, "
            f"错误码: {Style.RED(resp['errno'])}"
        )
