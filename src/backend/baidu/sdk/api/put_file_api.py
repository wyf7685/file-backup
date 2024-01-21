import asyncio
import json
from hashlib import md5
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.utils import Style, run_sync

from ..const import PATH_ROOT, BLOCK_SIZE
from ..exceptions import (
    BaiduUploadBlockError,
    BaiduUploadCreateError,
    BaiduUploadPrecreateError,
)
from ..openapi_client import ApiClient, ApiException
from ..openapi_client.api.fileupload_api import FileuploadApi
from ..sdk_config import config, get_logger


class BytesIOwithName(BytesIO):
    name: str


async def process_file(local_fp: Path) -> Tuple[int, List[bytes]]:
    """对文件进行切片, 分片大小为4MB

    :param local_fp: 本地文件路径
    """

    block_data = []
    file_size = 0
    with local_fp.open("rb") as f:
        read = run_sync(f.read)
        while block := await read(BLOCK_SIZE):
            block_data.append(block)
            file_size += len(block)

    return file_size, block_data


async def precreate(path: str, file_size: int, block_md5: List[str]) -> Dict[str, Any]:
    """文件预创建

    :param path: 远程文件路径
    :param file_size: 文件总大小(Byte)
    :param block_md5: 文件切片md5列表
    """

    with ApiClient() as client:
        return await run_sync(
            lambda: FileuploadApi(client).xpanfileprecreate(
                access_token=config.access_token,
                path=path,
                isdir=0,
                size=file_size,
                autoinit=1,
                block_list=json.dumps(block_md5),
                rtype=3,
            )
        )()


async def upload(
    partseq: int, path: str, upload_id: str, block: bytes
) -> Dict[str, Any]:
    """文件切片上传
    :param partseq: 文件切片编号
    :param path: 远程文件路径
    :param upload_id: 预上传接口获取的上传任务id
    :param block: 文件切片
    """

    file = BytesIOwithName(block)
    file.name = md5(block).hexdigest()

    with ApiClient() as client:
        return await run_sync(
            lambda: FileuploadApi(client).pcssuperfile2(
                access_token=config.access_token,
                partseq=str(partseq),
                path=path,
                uploadid=upload_id,
                type="tmpfile",
                file=file,
            )
        )()


async def create(
    path: str, file_size: int, upload_id: str, block_md5: List[str]
) -> Dict[str, Any]:
    """合并文件切片，创建远程文件

    :param path: 远程文件路径
    :param file_size: 远程文件大小(Byte)
    :param upload_id: 上传任务id
    :param block_list: 文件切片md5列表
    """
    with ApiClient() as client:
        return await run_sync(
            lambda: FileuploadApi(client).xpanfilecreate(
                access_token=config.access_token,
                path=path,
                isdir=0,
                size=file_size,
                uploadid=upload_id,
                block_list=json.dumps(block_md5),
                rtype=3,
            )
        )()


async def put_file(local_fp: Path, remote_fp: Path) -> None:
    """上传文件到百度网盘

    :param local_fp: 本地文件路径
    :param remote_fp: 远程文件路径"""
    logger = get_logger("put_file").opt(colors=True)
    file_size, block_data = await process_file(local_fp)
    block_md5 = [md5(i).hexdigest() for i in block_data]
    path = (PATH_ROOT / remote_fp).as_posix()

    # 预上传
    logger.debug(f"文件预上传: {Style.PATH_DEBUG(local_fp)}")
    try:
        precreate_resp = await precreate(path, file_size, block_md5)
    except ApiException as err:
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
        except ApiException as err:
            raise BaiduUploadBlockError(
                f"上传文件 {Style.PATH(path)} 切片({seq}) 时遇到错误:\n{Style.RED(err)}"
            ) from err

    await asyncio.gather(*[upload_block(seq) for seq in block_seq])

    # 创建文件
    logger.debug(f"远程合并切片文件: {Style.PATH_DEBUG(path)}")
    try:
        create_resp = await create(path, file_size, upload_id, block_md5)
    except ApiException as err:
        raise BaiduUploadCreateError(f"远程合并切片文件时遇到错误:\n{Style.RED(err)}") from err

    # 处理创建文件接口返回值
    if create_resp["errno"] != 0:
        raise BaiduUploadCreateError(
            f"远程合并切片文件 {Style.PATH_DEBUG(path)} 失败, "
            f"错误码: {Style.RED(create_resp['errno'])}"
        )
