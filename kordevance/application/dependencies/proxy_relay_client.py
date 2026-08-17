import os
from functools import lru_cache

from kordevance.adapters.http.proxy_relay_client import HttpProxyRelayClient
from kordevance.domain.ports.proxy_relay_client import ProxyRelayClient

_PROXY_RELAY_BASE_URL_ENV: str = "PROXY_RELAY_BASE_URL"


@lru_cache(maxsize=1)
def get_proxy_relay_client() -> ProxyRelayClient:
    base_url = os.environ.get(_PROXY_RELAY_BASE_URL_ENV)
    if not base_url:
        raise RuntimeError(f"{_PROXY_RELAY_BASE_URL_ENV} must be set to ProxyRelay's base URL")
    return HttpProxyRelayClient(base_url=base_url)
