from src.models import BaiduConfig, config as _config

config: BaiduConfig = _config.backend.baidu

_last_refresh: float = 0.0


def refresh_access_token() -> None:
    global _last_refresh
    import time
    from src.log import get_logger
    from src.utils import Style
    from . import openapi_client
    from .openapi_client.api import auth_api

    if time.time() - _last_refresh < 600:
        return

    logger = get_logger("Baidu:refresh_token").opt(colors=True)

    with openapi_client.ApiClient() as client:
        api = auth_api.AuthApi(client)
        try:
            resp = api.oauth_token_refresh_token(
                refresh_token=config.refresh_token,
                client_id="xmGaFeAxXEXX2fHu6Zds8iEaQcxPjsGn",
                client_secret="FA6bYyrtY3mYWr55B76nZyTXhzXVbyDY",
            )
        except openapi_client.ApiException as e:
            logger.error(f"刷新token时出现错误 {Style.RED(e)}")
            return

    config.access_token = resp["access_token"]
    config.refresh_token = resp["refresh_token"]
    _config.save()

    _last_refresh = time.time()

