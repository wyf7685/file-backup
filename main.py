import asyncio
import sys

from src import *


def greet() -> None:
    logger = get_logger("Main").opt(colors=True)
    logger.info(f"{Style.GREEN('file-backup')} 正在初始化...")
    logger.info(f"版本: {Style.GREEN(VERSION)}")
    logger.info(f"缓存目录: {Style.PATH(PATH.CACHE)}")
    logger.info(f"备份后端: {Style.CYAN(config.backend.type)}")
    logger.info(f"运行模式: [{Style.GREEN('Async')}]")


async def main_async() -> None:
    await BackupHost().start()
    await Console.start()


def main() -> None:
    logger = get_logger("Main").opt(colors=True)
    greet()

    try:
        asyncio.new_event_loop().run_until_complete(main_async())
    except KeyboardInterrupt:
        logger.warning("Interrupted")
    except Exception as e:
        logger.exception(f"{e.__class__.__name__}: {e}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
