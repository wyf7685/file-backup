from pathlib import Path

from qcloud_cos.cos_exception import CosClientError, CosServiceError  # type: ignore

from .config import ROOT


def put_file(local_fp: Path, remote_fp: Path, max_try: int = 3):
    from .config import client, bucket

    key = (ROOT / remote_fp).as_posix()
    local = local_fp.absolute().as_posix()

    err = None
    for _ in range(max_try):
        try:
            client.upload_file(Bucket=bucket, Key=key, LocalFilePath=local)  # type: ignore
            return
        except CosClientError or CosServiceError as e:
            err = e
    if err is not None:
        raise err
