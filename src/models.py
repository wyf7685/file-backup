import pathlib as _p

from pydantic import BaseModel

import src
from src.config import BackupConfig
from src.const import BackupUpdateType


class BackupRecord(BaseModel):
    uuid: str
    timestamp: float
    timestr: str


class BackupUpdate(BaseModel):
    type: BackupUpdateType
    """
    更新类型
    ----
    * file: 文件
    * dir: 文件夹
    * del: 移除
    """
    path: _p.Path
    """相对路径"""
    md5: str | None
    """
    * 文件: md5值
    * 文件夹/移除: None
    """


def find_backup(name: str) -> BackupConfig | None:
    if data := [i for i in src.config.backup_list if i.name == name]:
        return data[0]
