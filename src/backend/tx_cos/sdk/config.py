import logging
from pathlib import Path

from qcloud_cos import CosConfig, CosS3Client  # type: ignore

from src.log import LoguruHandler

qcloud_cos_logger = logging.getLogger("qcloud_cos")
qcloud_cos_logger.handlers = [LoguruHandler()]
qcloud_cos_logger.propagate = False
qcloud_cos_logger.level = logging.WARNING

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
