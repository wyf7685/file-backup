from ...config import BaiduConfig
from ...config import config as _config

config: BaiduConfig = _config.baidu

_refreshing: bool = False


def get_logger(name: str):
    from src.log import get_logger

    return get_logger(f"Baidu::{name}")


async def refresh_access_token() -> None:
    import asyncio
    import time

    global _refreshing
    while _refreshing:
        await asyncio.sleep(0.1)
    _refreshing = True

    if time.time() < config.expire - 600:
        return

    from src.utils import Style, run_sync

    from .openapi_client import ApiClient, ApiException
    from .openapi_client.api.auth_api import AuthApi

    logger = get_logger("refresh_token").opt(colors=True)
    logger.debug("刷新 access_token")

    with ApiClient() as client:
        call = run_sync(AuthApi(client).oauth_token_refresh_token)
        try:
            resp = await call(
                refresh_token=config.refresh_token,
                client_id=config.app_id,
                client_secret=config.app_secret,
            )
        except ApiException as e:
            logger.error(f"刷新token时出现错误 {Style.RED(e)}")
            return

    config.access_token = resp["access_token"]
    config.refresh_token = resp["refresh_token"]
    config.expire = int(time.time() + resp["expires_in"])
    _config.save()
    _refreshing = False
