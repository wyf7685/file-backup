from .config import Config as Config
from .config import init_config as _init
from .config import BackupConfig as BackupConfig
from .config_model import ConfigModel as ConfigModel

config = _init()
