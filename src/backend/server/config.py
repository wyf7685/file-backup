from typing import ClassVar

from pydantic import BaseModel, Field


class Config(BaseModel):
    __backend_name__: ClassVar[str] = "server"
    url: str = Field(default="http://127.0.0.1:8008")
    token: str = Field(default="token")
    api_key: str = Field(default="api_key")
