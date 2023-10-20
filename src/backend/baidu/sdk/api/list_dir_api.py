from pathlib import Path
from typing import List, Tuple

from src.log import get_logger
from src.utils import Style, run_sync

from .. import openapi_client
from ..const import *
from ..exceptions import BaiduListDirectoryError
from ..openapi_client.api import multimediafile_api
from ..sdk_config import config


async def listall(path: str):
    with openapi_client.ApiClient() as client:
        api = multimediafile_api.MultimediafileApi(client)
        call = lambda: api.xpanfilelistall(
            access_token=config.access_token,
            path=path,
            recursion=0,
            web="0",
            start=0,
            limit=1000,
            order="time",
        )
        resp = await run_sync(call)()
    return resp


async def list_dir(path: Path) -> List[Tuple[str, str]]:
    logger = get_logger("Baidu:list_dir").opt(colors=True)
    logger.debug(f"列出目录: {Style.PATH_DEBUG(path)}")

    try:
        resp = await listall(str(PATH_ROOT / path).replace("\\", "/"))
    except openapi_client.ApiException as err:
        raise BaiduListDirectoryError(
            f"列出目录 {Style.PATH(path)} 时遇到错误:\n{Style.RED(err)}"
        ) from err

    if resp["errno"] != 0:
        raise BaiduListDirectoryError(
            f"列出目录 {Style.PATH(path)} 失败, "
            f"错误码: {Style.RED(resp['errno'])}"
        )

    return [
        ("d" if item["isdir"] else "f", item["server_filename"])
        for item in resp["list"]
    ]
