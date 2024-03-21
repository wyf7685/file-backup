import logging
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client  # type: ignore

from src.log import LoguruHandler

_logger = logging.getLogger("qcloud_cos")
_logger.handlers = [LoguruHandler()]
_logger.propagate = False
_logger.level = logging.WARNING

ROOT = Path("storage")
bucket: str = ""
client: CosS3Client = None  # type: ignore


def init_client(secret_id: str, secret_key: str, region: str, bucket_: str):
    global bucket, client
    bucket = bucket_
    client = CosS3Client(
        CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Token=None,
            Scheme="https",
        )
    )
