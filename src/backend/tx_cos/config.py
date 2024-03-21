from typing import ClassVar

from pydantic import BaseModel, Field


class Config(BaseModel):
    __backend_name__: ClassVar[str] = "tx_cos"
    secret_id: str = Field(default="SECRET_ID")
    secret_key: str = Field(default="SECRET_KEY")
    region: str = Field(default="REGION")
    bucket: str = Field(default="BUCKET")
