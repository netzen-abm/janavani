"""Server-only Supabase configuration and client construction."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    service_role_key: str


def load_supabase_config() -> SupabaseConfig:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for Supabase mode")
    if not url.startswith(("https://", "http://")):
        raise RuntimeError("SUPABASE_URL must be an HTTP(S) URL")
    return SupabaseConfig(url=url, service_role_key=key)


def build_supabase_client() -> Any:
    config = load_supabase_config()
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("Supabase mode requires the supabase Python package") from exc
    return create_client(config.url, config.service_role_key)
