# src/services/storage_adapter.py
"""Storage adapter layer.
Provides a small interface to write entries to the chosen storage backend.
Default backend: 'jsonl' (local JSONL file). Optional: 'supabase' if configured.

This keeps storage swappable and centralizes error handling and directory preparation.
"""

import os
import json
from typing import Dict, Any

# Optional supabase client - import lazily to avoid hard dependency at module import time
try:
    from database.supabase import supabase
except Exception:
    supabase = None


STORAGE_BACKEND = os.getenv("JANAVANI_STORAGE_BACKEND", "jsonl").lower()
JSONL_PATH = os.getenv("JANAVANI_RATINGS_JSONL", "database/ratings.jsonl")


def _ensure_db_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def save_rating_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Save a rating/complaint entry to the configured backend.

    Returns a dict with keys: success (bool), message (str)
    """
    backend = STORAGE_BACKEND

    if backend == "supabase":
        if supabase is None:
            return {"success": False, "message": "Supabase backend selected but not configured."}
        try:
            # supabase client expected to follow .table().insert().execute() pattern
            res = supabase.table("ratings").insert(entry).execute()
            if getattr(res, "error", None):
                return {"success": False, "message": f"Supabase insert error: {res.error}"}
            return {"success": True, "message": "Saved to Supabase."}
        except Exception as e:
            return {"success": False, "message": f"Supabase save failed: {e}"}

    # Default: jsonl
    try:
        _ensure_db_dir(JSONL_PATH)
        with open(JSONL_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        return {"success": True, "message": f"Saved to {JSONL_PATH}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to save to jsonl: {e}"}
