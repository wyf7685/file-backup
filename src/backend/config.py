from pathlib import Path

from pydantic import BaseModel, Field

from src.config import ConfigModel
from src.config import config as global_config
from src.const import BackendType


class LocalConfig(BaseModel):
    storage: Path = Field(default=Path("backup"))


class ServerConfig(BaseModel):
    url: str = Field(default="http://127.0.0.1:8008")
    token: str = Field(default="token")
    api_key: str = Field(default="api_key")


class BaiduConfig(BaseModel):
    app_id: str = Field(default="app_id")
    app_secret: str = Field(default="app_secret")
    access_token: str = Field(default="access_token")
    refresh_token: str = Field(default="refresh_token")
    expire: int = Field(default=0)


class BackendConfig(BaseModel):
    type: BackendType = Field(default="local")
    local: LocalConfig = Field(default_factory=LocalConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    baidu: BaiduConfig = Field(default_factory=BaiduConfig)

    def save(self):
        global_config.save()


class Config(ConfigModel):
    backend: BackendConfig = Field(default_factory=BackendConfig)


config = global_config.parse_config(Config).backend
