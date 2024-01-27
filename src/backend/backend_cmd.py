from typing import List
from src.console import Console
from src.utils import Style
from src.const.exceptions import CommandExit

from .config import config, Config, global_config


@Console.register("backend", "查询/修改备份后端", arglen=[0, 1])
async def cmd_backend(args: List[str]):
    logger = cmd_backend.logger

    if not args:
        logger.info(f"当前备份后端: {Style.CYAN(config.type)}")
        return

    from . import get_backend

    [name] = args
    try:
        backend = get_backend(name)
    except Exception as err:
        raise CommandExit(f"不存在名为 {Style.CYAN(name)} 的 Backend", True) from err
    
    root = global_config.parse_config(Config)
    root.backend.type = name # type: ignore
    root.save()

    logger.debug(f"Backend: {backend!r}")
    logger.success(f"备份后端更改为: {Style.CYAN(name)}")
