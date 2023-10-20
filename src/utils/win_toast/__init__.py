import asyncio
from typing import Literal, TypeAlias

from win11toast import toast_async

from src.const import PATH
from src.log import get_logger

DurationType: TypeAlias = Literal["short", "long"]

ICON = {
    "src": "",
    "placement": "appLogoOverride",
    "hint-crop": "circle",
}


def _init_icon() -> None:
    from base64 import b64decode

    from .raw_icon import ICON_RAW

    icon_path = PATH.CACHE / "shell32_172.ico"
    icon_path.write_bytes(b64decode(ICON_RAW))

    ICON["src"] = str(icon_path.absolute())


async def notify(
    title: str, body: str, *, duration: DurationType = "short", block: bool = False
) -> None:
    from src.models import config
    
    if not config.experiment.enable_notify:
        return
    
    logger = get_logger("Toast")

    args = {
        "title": title,
        "body": body,
        "duration": duration,
        "icon": ICON.copy(),
        "app_id": "file-backup",
        "on_click": lambda x: logger.debug(f"Toast clicked: {x}"),
        "on_dismissed": lambda x: logger.debug(f"Toast dismissed: {x}"),
        "on_failed": lambda x: logger.debug(f"Toast failed: {x}"),
    }

    coro = toast_async(**args)

    if block:
        await coro
    else:
        asyncio.get_running_loop().create_task(coro)


_init_icon()
