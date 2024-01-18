from ._config import Config as Config
from ._config import init_config as _init
from ._config import BackupConfig as BackupConfig
from .config_model import ConfigModel as ConfigModel

config = _init()
