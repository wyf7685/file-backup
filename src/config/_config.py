from pathlib import Path
from typing import List

from hashlib import md5
from pydantic import BaseModel, Field

from src.const import BackupMode
from src.utils import Style

from .config_model import ConfigModel


class BackupConfig(BaseModel):
    name: str
    mode: BackupMode
    local_path: Path
    interval: int

    def get_remote(self) -> Path:
        return Path(md5(self.name.encode()).hexdigest())


class ExperimentConfig(BaseModel):
    log_html: bool = Field(default=False)


class Config(ConfigModel):
    log_level: str = Field(default="INFO")
    experiment: ExperimentConfig = Field(default_factory=ExperimentConfig)
    backup_list: List[BackupConfig] = Field(default_factory=list)


def init_config() -> Config:
    from src.log import get_logger, set_log_level

    logger = get_logger("Config").opt(colors=True)
    config = Config.load()

    set_log_level(config.log_level)

    is_experiment = False
    for key in config.experiment.model_fields.keys():
        if getattr(config.experiment, key, False):
            logger.warning(f"实验性功能 {Style.YELLOW(key)} 已启用")
            is_experiment = True

    if is_experiment:
        logger.warning("启用实验性功能可能会产生意料之外的结果, 请谨慎使用")

    return config
