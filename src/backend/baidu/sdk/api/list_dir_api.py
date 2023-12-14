from pathlib import Path
from typing import List, Tuple

from src.utils import Style, run_sync

from ..const import *
from ..exceptions import BaiduListDirectoryError
from ..openapi_client import ApiClient, ApiException
from ..openapi_client.api.multimediafile_api import MultimediafileApi
from ..sdk_config import config, get_logger


async def listall(path: str):
    with ApiClient() as client:
        return await run_sync(
            lambda: MultimediafileApi(client).xpanfilelistall(
                access_token=config.access_token,
                path=path,
                recursion=0,
                web="0",
                start=0,
                limit=1000,
                order="time",
            )
        )()


async def list_dir(path: Path) -> List[Tuple[str, str]]:
    logger = get_logger("list_dir").opt(colors=True)
    logger.debug(f"列出目录: {Style.PATH_DEBUG(path)}")

    try:
        resp = await listall(str(PATH_ROOT / path).replace("\\", "/"))
    except ApiException as err:
        raise BaiduListDirectoryError(
            f"列出目录 {Style.PATH(path)} 时遇到错误:\n{Style.RED(err)}"
        ) from err

    if resp["errno"] != 0:
        raise BaiduListDirectoryError(
            f"列出目录 {Style.PATH(path)} 失败, " f"错误码: {Style.RED(resp['errno'])}"
        )

    return [
        ("d" if item["isdir"] else "f", item["server_filename"])
        for item in resp["list"]
    ]
