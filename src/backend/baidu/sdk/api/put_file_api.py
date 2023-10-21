import asyncio
import json
import os
from hashlib import md5
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Tuple

import aiofiles

from src.const import PATH
from src.log import get_logger
from src.utils import Style, run_sync

from .. import openapi_client
from ..const import *
from ..exceptions import (BaiduUploadBlockError, BaiduUploadCreateError,
                          BaiduUploadPrecreateError)
from ..openapi_client.api import fileupload_api
from ..sdk_config import config


async def process_file(local_fp: Path) -> Tuple[int, List[bytes]]:
    """对文件进行切片, 分片大小为4MB"""
    async with aiofiles.open(local_fp, "rb") as f:
        content = await f.read()
    file_size = len(content)

    block_data = []
    i = 0
    while len(content) > BLOCK_SIZE:
        start, end = i * BLOCK_SIZE, (i + 1) * BLOCK_SIZE
        block_data.append(content[start:end])
        content = content[end:]
    block_data.append(content)

    return file_size, block_data


async def precreate(path: str, file_size: int, block_list: List[str]) -> Dict[str, Any]:
    with openapi_client.ApiClient() as client:
        api = fileupload_api.FileuploadApi(client)
        call = lambda: api.xpanfileprecreate(
            access_token=config.access_token,
            path=path,
            isdir=0,
            size=file_size,
            autoinit=1,
            block_list=json.dumps(block_list),
            rtype=3,
        )
        resp = await run_sync(call)()
    return resp


async def upload(
    partseq: int, path: str, upload_id: str, block: bytes
) -> Dict[str, Any]:
    cache_fp = PATH.CACHE / md5(block).hexdigest()

    async with aiofiles.open(cache_fp, "wb") as f:
        await f.write(block)

    with openapi_client.ApiClient() as client:
        api = fileupload_api.FileuploadApi(client)
        call = lambda: api.pcssuperfile2(
            access_token=config.access_token,
            partseq=str(partseq),
            path=path,
            uploadid=upload_id,
            type="tmpfile",
            file=cache_fp.open("rb"),
        )
        resp = await run_sync(call)()
    os.remove(cache_fp)
    
    return resp


async def create(
    path: str, file_size: int, upload_id: str, block_list: List[str]
) -> Dict[str, Any]:
    with openapi_client.ApiClient() as client:
        api = fileupload_api.FileuploadApi(client)
        call = lambda: api.xpanfilecreate(
            access_token=config.access_token,
            path=path,
            isdir=0,
            size=file_size,
            uploadid=upload_id,
            block_list=json.dumps(block_list),
            rtype=3,
        )
        resp = await run_sync(call)()
    return resp


async def put_file(local_fp: Path, remote_fp: Path) -> None:
    logger = get_logger("Baidu:put_file").opt(colors=True)
    file_size, block_data = await process_file(local_fp)
    block_md5 = [md5(i).hexdigest() for i in block_data]
    path = str(PATH_ROOT / remote_fp).replace("\\", "/")

    # 预上传
    logger.debug(f"文件预上传: {Style.PATH_DEBUG(local_fp)}")
    try:
        precreate_resp = await precreate(path, file_size, block_md5)
    except openapi_client.ApiException as err:
        raise BaiduUploadPrecreateError(
            f"预上传文件 {Style.PATH(local_fp)} 时遇到错误:\n{Style.RED(err)}"
        ) from err

    # 处理预上传接口返回值
    if precreate_resp["errno"] != 0:
        raise BaiduUploadPrecreateError(
            f"预上传文件 {Style.PATH(local_fp)} 失败, "
            f"错误码: {Style.RED(precreate_resp['errno'])}"
        )
    upload_id: str = precreate_resp["uploadid"]
    block_seq: List[int] = precreate_resp["block_list"]

    # 上传切片
    async def upload_block(seq: int):
        logger.debug(f"上传文件切片: seq={Style.YELLOW(seq)}")
        try:
            await upload(seq, path, upload_id, block_data[seq])
        except openapi_client.ApiException as err:
            raise BaiduUploadBlockError(
                f"上传文件 {Style.PATH(path)} 切片({seq}) 时遇到错误:\n{Style.RED(err)}"
            ) from err
    await asyncio.gather(*[upload_block(seq) for seq in block_seq])

    # 创建文件
    logger.debug(f"远程合并切片文件: {Style.PATH_DEBUG(path)}")
    try:
        create_resp = await create(path, file_size, upload_id, block_md5)
    except openapi_client.ApiException as err:
        raise BaiduUploadCreateError(f"远程合并切片文件时遇到错误:\n{Style.RED(err)}") from err

    # 处理创建文件接口返回值
    if create_resp["errno"] != 0:
        raise BaiduUploadCreateError(
            f"远程合并切片文件 {Style.PATH_DEBUG(path)} 失败, "
            f"错误码: {Style.RED(create_resp['errno'])}"
        )
