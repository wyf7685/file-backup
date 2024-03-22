import asyncio
import sys

from src import PATH, VERSION, BackupHost, Console, Style, get_logger


def greet():
    from src.backend import get_backend
    from src.backend.config import config as backend_config

    logger = get_logger("Main").opt(colors=True)
    logger.info(f"{Style.GREEN("file-backup")} 正在初始化...")
    logger.info(f"版本: {Style.GREEN(VERSION)}")
    logger.info(f"配置文件: {Style.PATH(PATH.CONFIG)}")
    logger.info(f"缓存目录: {Style.PATH(PATH.CACHE)}")
    logger.info(f"备份后端: {Style.CYAN(backend_config.type)}")
    logger.debug(f"备份后端类: {Style.CYAN(get_backend(), fix=False)}")
    return logger


async def main_async() -> None:
    await asyncio.gather(BackupHost.start(), Console.start())


def main() -> None:
    logger = greet()

    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.warning("Interrupted")
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}: {e}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
