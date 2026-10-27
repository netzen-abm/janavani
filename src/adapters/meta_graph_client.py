"""Outbound transport for Meta Graph API messaging.

Channel adapters construct provider-specific payloads and retain their own
credentials. This module owns only shared HTTP mechanics.
"""
import logging
import os
import re
from typing import Any, Mapping, Optional

import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger("janavani.adapters.meta_graph_client")
_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_maxsize=10))


def send_meta_message(
    object_id: str,
    access_token: Optional[str],
    payload: Mapping[str, Any],
    http_session: Optional[requests.Session] = None,
) -> bool:
    """Send a provider-shaped message payload without logging its contents."""
    if not object_id or not access_token:
        return False

    version = os.getenv("META_GRAPH_API_VERSION", "v26.0")
    if not re.fullmatch(r"v[0-9]+\.[0-9]+", version):
        logger.error("META_GRAPH_API_VERSION has an invalid format")
        return False

    session = http_session or _session
    url = f"https://graph.facebook.com/{version}/{object_id}/messages"
    try:
        response = session.post(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            json=dict(payload),
            timeout=(2, 5),
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.warning("Meta Graph API message delivery failed")
        return False
    return True
