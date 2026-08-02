# Nym proxy helper: route HTTP(S) requests through a local Nym SOCKS5 proxy

import os
import requests

NYM_SOCKS = os.getenv("NYM_SOCKS", "socks5h://127.0.0.1:1080")
PROXIES = {"http": NYM_SOCKS, "https": NYM_SOCKS}


def get_via_nym(url: str, timeout: int = 15) -> bytes:
    r = requests.get(url, proxies=PROXIES, timeout=timeout)
    r.raise_for_status()
    return r.content


def post_via_nym(url: str, data=None, json_payload=None, timeout: int = 20):
    r = requests.post(url, data=data, json=json_payload, proxies=PROXIES, timeout=timeout)
    r.raise_for_status()
    return r
