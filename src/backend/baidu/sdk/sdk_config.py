from typing import ClassVar

from pydantic import BaseModel, Field

from ...config import parse_config, save_config


class Config(BaseModel):
    __backend_name__: ClassVar[str] = "baidu"
    app_id: str = Field(default="app_id")
    app_secret: str = Field(default="app_secret")
    access_token: str = Field(default="access_token")
    refresh_token: str = Field(default="refresh_token")
    expire: int = Field(default=0)

    def save(self):
        save_config(self)


def get_logger(name: str):
    from src.log import get_logger

    return get_logger(f"Baidu::{name}")


config: Config = parse_config(Config)
