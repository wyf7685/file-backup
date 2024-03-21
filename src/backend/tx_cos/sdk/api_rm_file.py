from pathlib import Path

from .config import ROOT


def rm_file(path: Path):
    from .config import client, bucket

    client.delete_object(Bucket=bucket, Key=(ROOT / path).as_posix()) # type: ignore
