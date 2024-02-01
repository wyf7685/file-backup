from typing import Dict, Self, Tuple, Type, cast, override

from pydantic import BaseModel, Field

from src.config import ConfigModel
from src.config import config as global_config
from src.const import BackendType


class BackendConfig(ConfigModel):
    type: BackendType = Field(default="local")

    @override
    def save(self) -> Self:
        global_config.save()
        return self


class Config(ConfigModel):
    backend: BackendConfig = Field(default_factory=BackendConfig)


config = global_config.parse_config(Config).backend


def _mix_model[T](name: str, base: Type[T], attr: Dict[str, type]) -> Type[T]:
    attrs = {k: Field(default_factory=v) for k, v in attr.items()}
    attrs |= {"__annotations__": attr}
    return cast(Type[T], type(name, (base,), attrs))


def _mix_config[T](config_cls: type) -> Tuple[str, Config]:
    name = getattr(config_cls, "__backend_name__", None)
    assert name is not None, "Backend 的 Config 类必须拥有 __backend_name__ 属性"

    MixedBackend = _mix_model(config_cls.__name__, BackendConfig, {name: config_cls})
    MixedConfig = _mix_model("Config", Config, {"backend": MixedBackend})

    return name, global_config.parse_config(MixedConfig)


def parse_config[T](config_cls: Type[T]) -> T:
    name, parsed = _mix_config(config_cls)
    return getattr(parsed.backend, name)


def save_config(config: BaseModel) -> None:
    name, parsed = _mix_config(config.__class__)
    setattr(parsed.backend, name, config)
    parsed.save()
