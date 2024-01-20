from typing import Self, Type

from pydantic import BaseModel

from src.const import PATH
from src.log import get_logger
from src.utils import Style


class ConfigModel(BaseModel):
    class Config:
        extra = "allow"

    def save(self) -> Self:
        data = self.model_dump_json(indent=4)
        PATH.CONFIG.write_text(
            data=data,
            encoding="utf-8",
        )
        return self

    @classmethod
    def load(cls, *, silent: bool = False) -> Self:
        logger = get_logger("Config").opt(colors=True)
        config = cls()
        if not silent:
            logger.opt(colors=True).info(f"配置文件路径: {Style.PATH(PATH.CONFIG)}")

        if PATH.CONFIG.exists():
            try:
                config_json = PATH.CONFIG.read_text(encoding="utf-8")
                config = cls.model_validate_json(config_json)
            except Exception as err:
                logger.exception(f"解析配置文件时发生错误: {Style.RED(err)}")
                logger.error("自动恢复至默认配置文件")
                fp = PATH.DATA / "config.json.bak"
                try:
                    PATH.CONFIG.rename(fp)
                    logger.error(f"原配置文件: {Style.PATH(fp)}")
                except Exception as err:
                    logger.exception(f"转存原配置文件时发生错误: {Style.RED(err)}")
        else:
            logger.info("配置文件不存在, 创建默认配置文件...")

        config.save()
        return config

    @classmethod
    def parse_config[T: BaseModel](cls, model_cls: Type[T]) -> T:
        return type(model_cls.__name__, (cls, model_cls), {}).load(silent=True)  # type: ignore
