import time

from src.utils import Style, run_sync

from ..openapi_client import ApiClient, ApiException
from ..openapi_client.api.auth_api import AuthApi
from ..sdk_config import config, get_logger

_refreshing: bool = False


async def refresh_token() -> None:
    global _refreshing
    if _refreshing or time.time() < config.expire - 600:
        return
    _refreshing = True

    logger = get_logger("refresh_token").opt(colors=True)
    logger.debug("刷新 access_token")

    with ApiClient() as client:
        call = run_sync(AuthApi(client).oauth_token_refresh_token)  # type: ignore
        try:
            resp = await call(  # type: ignore
                refresh_token=config.refresh_token,
                client_id=config.app_id,
                client_secret=config.app_secret,
            )
        except ApiException as e:
            logger.error(f"刷新token时出现错误 {Style.RED(e)}")
            return

    config.access_token = resp["access_token"]
    config.refresh_token = resp["refresh_token"]
    config.expire = int(time.time() + resp["expires_in"])  # type: ignore
    config.save()
    _refreshing = False
