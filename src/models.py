import contextlib
from hashlib import md5 as _md5
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from src.const import *
from src.utils import Style


class LocalConfig(BaseModel):
    storage: Path = Field(default=Path("backup"))


class ServerConfig(BaseModel):
    url: str = Field(default="http://127.0.0.1:8008")
    token: str = Field(default="token")


class BaiduConfig(BaseModel):
    access_token: str = Field(default="access_token")
    refresh_token: str = Field(default="refresh_token")


class BackendConfig(BaseModel):
    type: BackendType = Field(default="local")
    local: LocalConfig = Field(default_factory=LocalConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    baidu: BaiduConfig = Field(default_factory=BaiduConfig)


class BackupConfig(BaseModel):
    name: str
    mode: BackupMode
    local_path: Path
    interval: int

    def get_remote(self) -> Path:
        return Path(_md5(self.name.encode()).hexdigest())


class ExperimentConfig(BaseModel):
    log_html: bool = Field(default=False)


class Config(BaseModel):
    log_level: str = Field(default="INFO")
    backend: BackendConfig = Field(default_factory=BackendConfig)
    experiment: ExperimentConfig = Field(default_factory=ExperimentConfig)
    backup_list: List[BackupConfig] = Field(default_factory=list)

    def save(self, path: Path = PATH.CONFIG) -> None:
        path.write_text(self.model_dump_json(indent=4))

    def reload(self) -> "Config":
        config = _init_config()
        for attr in list(self.model_fields):
            setattr(self, attr, getattr(config, attr))
        return self


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
    md5: Optional[str]
    """
    * 文件: md5值
    * 文件夹/移除: None
    """

    def check(self, md5: str) -> bool:
        return self.md5 == md5


def find_backup(name: str) -> Optional[BackupConfig]:
    if data := [i for i in config.backup_list if i.name == name]:
        return data[0]


def _init_config() -> Config:
    from src.log import get_logger, set_log_level

    logger = get_logger("Config").opt(colors=True)
    config = Config()

    if PATH.CONFIG.exists():
        try:
            config_json = PATH.CONFIG.read_text(encoding="utf-8")
            config = Config.model_validate_json(config_json)
        except Exception as e:
            logger.exception(f"解析配置文件时发生错误: {Style.RED(e)}")
            fp = PATH.DATA / "config.json.bak"
            with contextlib.suppress(Exception):
                PATH.CONFIG.rename(fp)
            logger.error("自动恢复至默认配置文件")
            logger.error(f"原配置文件: {Style.PATH(fp)}")
    config.save()

    set_log_level(config.log_level)

    is_experiment = False
    for key in config.experiment.model_fields.keys():
        if getattr(config.experiment, key, False):
            logger.warning(f"实验性功能 {Style.YELLOW(key)} 已启用")
            is_experiment = True

    if is_experiment:
        logger.warning("启用实验性功能可能会产生意料之外的结果, 请谨慎使用")

    return config


config = _init_config()
