import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import aiohttp

from src.log import get_logger
from src.utils import Style, run_sync

from .. import openapi_client
from ..const import *
from ..exceptions import BaiduGetFileError, BaiduListDirectoryError
from ..openapi_client.api import multimediafile_api
from ..sdk_config import config
from .list_dir_api import listall


async def filemetas(fsid: int):
    with openapi_client.ApiClient() as client:
        api = multimediafile_api.MultimediafileApi(client)
        call = lambda: api.xpanmultimediafilemetas(
            access_token=config.access_token,
            fsids=json.dumps([fsid]),
            thumb="0",
            extra="0",
            dlink="1",
            needmedia=0,
        )
        resp = await run_sync(call)()
    return resp


def get_fsid(file_list: List[Dict[str, Any]], file_name: str) -> Optional[int]:
    for item in file_list:
        if item["server_filename"] == file_name:
            return item["fs_id"]


async def get_file(local_fp: Path, remote_fp: Path):
    logger = get_logger("Baidu:get_file").opt(colors=True)
    path = PATH_ROOT / remote_fp

    logger.debug(f"获取目录文件清单: {Style.PATH_DEBUG(remote_fp.parent)}")
    try:
        listall_resp = await listall(str(path.parent).replace("\\", "/"))
    except openapi_client.ApiException as err:
        raise BaiduListDirectoryError(
            f"获取网盘 {Style.PATH(remote_fp.parent)} 文件清单时遇到错误:\n{Style.RED(err)}"
        ) from err

    if listall_resp["errno"] != 0:
        raise BaiduListDirectoryError(
            f"列出目录 {Style.PATH(path)} 失败, 错误码: {Style.RED(listall_resp['errno'])}"
        )

    fsid = get_fsid(listall_resp["list"], path.name)
    if fsid is None:
        raise BaiduGetFileError(f"获取文件 {Style.PATH(remote_fp)} 的fsid失败: 文件不存在")
    logger.debug(f"获取文件fsid: {Style.GREEN(fsid)}")

    logger.debug(f"获取文件信息: {Style.PATH_DEBUG(remote_fp)}")
    try:
        filemetas_resp = await filemetas(fsid)
    except openapi_client.ApiException as err:
        # if isinstance(err.body, bytes) and err.body.decode('utf-8'):

        raise BaiduGetFileError(
            f"获取 {Style.PATH(remote_fp)} 文件信息时遇到错误:\n{Style.RED(err)}"
        ) from err

    if filemetas_resp["errno"] != 0:
        raise BaiduGetFileError(
            f"获取 {Style.PATH(remote_fp)} 文件信息失败, "
            f"错误码: {Style.RED(filemetas_resp['errno'])}"
        )

    dlink = filemetas_resp["list"][0]["dlink"]  # type: str
    logger.debug(f"获取文件下载链接: {Style.PATH_DEBUG(dlink)}")
    dlink += f"&access_token={config.access_token}"

    logger.debug(f"下载文件: {Style.PATH_DEBUG(dlink)}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(dlink) as resp:
                data = await resp.read()
    except aiohttp.ClientError as err:
        raise BaiduGetFileError(
            f"下载 {Style.PATH(remote_fp)} 时遇到错误:\n{Style.RED(err)}"
        ) from err

    logger.debug(f"写入: {Style.PATH_DEBUG(local_fp)}")
    local_fp.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with aiofiles.open(local_fp, "wb") as f:
            await f.write(data)
    except Exception as err:
        raise BaiduGetFileError(
            f"写入 {Style.PATH(local_fp)} 时遇到错误:\n{Style.RED(err)}"
        ) from err
    
