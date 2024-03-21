from pathlib import Path

from qcloud_cos.cos_exception import CosClientError, CosServiceError  # type: ignore

from .config import ROOT


def get_file(local_fp: Path, remote_fp: Path, max_try: int = 3):
    from .config import client, bucket

    err = None
    for _ in range(max_try):
        try:
            client.download_file(  # type: ignore
                Bucket=bucket,
                Key=(ROOT / remote_fp).as_posix(),
                DestFilePath=local_fp.absolute().as_posix(),
            )
            return
        except CosClientError or CosServiceError as e:
            err = e
    if err is not None:
        raise err
