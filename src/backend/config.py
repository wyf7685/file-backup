from typing import Tuple, Type

from pydantic import BaseModel, Field

from src.config import ConfigModel
from src.config import config as global_config
from src.const import BackendType


class BackendConfig(ConfigModel):
    type: BackendType = Field(default="local")

    def save(self):
        global_config.save()


class Config(ConfigModel):
    backend: BackendConfig = Field(default_factory=BackendConfig)


config = global_config.parse_config(Config).backend


def _mix_config(config_cls: Type) -> Tuple[str, Config]:
    name = getattr(config_cls, "__backend_name__", None)
    assert name is not None, "Backend 的 Config 类必须拥有 __backend_name__ 属性"
    Mixed = type(
        config_cls.__name__,
        (BackendConfig,),
        {
            "__annotations__": {name: config_cls},
            name: Field(default_factory=config_cls),
        },
    )

    return name, global_config.parse_config(
        type(
            "Config",
            (ConfigModel,),
            {
                "__annotations__": {"backend": Mixed},
                "backend": Field(default_factory=Mixed),  # type: ignore
            },
        )
    )


def parse_config[T](config_cls: Type[T]) -> T:
    name, parsed = _mix_config(config_cls)
    return getattr(parsed.backend, name)


def save_config(config: BaseModel) -> None:
    name, parsed = _mix_config(config.__class__)
    setattr(parsed.backend, name, config)
    parsed.save()
