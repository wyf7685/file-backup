from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field


class Config(BaseModel):
    __backend_name__: ClassVar[str] = "local"
    storage: Path = Field(default=Path("backup"))

