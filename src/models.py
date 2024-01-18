import typing as _t
from pathlib import Path

from pydantic import BaseModel

from src.config import BackupConfig, config
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
    path: Path
    """相对路径"""
    md5: _t.Optional[str]
    """
    * 文件: md5值
    * 文件夹/移除: None
    """


def find_backup(name: str) -> _t.Optional[BackupConfig]:
    if data := [i for i in config.backup_list if i.name == name]:
        return data[0]
