# src/services/search_directory.py
"""
Finds govt offices from CSV with a light in-process cache and robust error handling.
This reduces repeated pandas.read_csv costs and prevents crashing on missing/corrupt files.
"""

import os
import threading
import time
from typing import Optional

import pandas as pd

_DATABASE_PATH = os.getenv("JANAVANI_OFFICES_CSV", "database/offices.csv")
_CACHE_LOCK = threading.Lock()
_CACHE: Optional[pd.DataFrame] = None
_CACHE_MTIME: Optional[float] = None
_CACHE_LOADED_AT: Optional[float] = None


def _load_offices(force: bool = False) -> Optional[pd.DataFrame]:
    """Load offices CSV into module cache. Reloads if file changed on disk.

    Returns DataFrame or None on failure.
    """
    global _CACHE, _CACHE_MTIME, _CACHE_LOADED_AT

    try:
        if not os.path.exists(_DATABASE_PATH):
            return None

        mtime = os.path.getmtime(_DATABASE_PATH)

        # Fast path: cached and unchanged
        if not force and _CACHE is not None and _CACHE_MTIME == mtime:
            return _CACHE

        # Acquire lock to reload safely
        with _CACHE_LOCK:
            # double-check after acquiring
            if not force and _CACHE is not None and _CACHE_MTIME == mtime:
                return _CACHE

            # Read CSV with conservative options
            df = pd.read_csv(_DATABASE_PATH, dtype=str, keep_default_na=False)

            # Normalize expected columns if present
            expected = ["id", "name", "type", "address", "city", "officer_role", "email"]
            for col in expected:
                if col not in df.columns:
                    df[col] = ""

            # Cache
            _CACHE = df
            _CACHE_MTIME = mtime
            _CACHE_LOADED_AT = time.time()
            return _CACHE

    except Exception:
        # Avoid raising: caller will handle None and return user-friendly message
        return None


def search_office(query: str, city: str = "Kochi") -> str:
    """
    Input: query="ration shop", city="Kochi"
    Output: short textual list of offices (capped)
    """
    if not query or not query.strip():
        return "Invalid search query. Provide the department or office type."

    df = _load_offices()
    if df is None:
        return f"Office database not found or unreadable. Expected at: {_DATABASE_PATH}"

    try:
        # Perform case-insensitive contains search on limited columns
        q = query.strip()
        c = city.strip()

        # Use vectorized operations with na handling
        mask_type = df["type"].str.contains(q, case=False, na=False)
        mask_city = df["city"].str.contains(c, case=False, na=False)

        results = df[mask_type & mask_city]

        if results.empty:
            return f"No {q} found in {c}. You can add it to { _DATABASE_PATH }"

        output = f"Found {len(results)} {q}(s) in {c}:\n\n"

        # Cap results to 5 for UI/telegram friendliness
        for _, row in results.head(5).iterrows():
            output += f"ID: {row['id']}\n"
            output += f"Name: {row['name']}\n"
            output += f"Address: {row['address']}\n"
            output += f"Officer: {row['officer_role']}\n"
            output += f"Email: {row['email']}\n"
            output += "---\n"

        output += "\nReply with the ID to file a complaint."
        return output

    except Exception:
        return "Search failed due to an internal error. Please contact the administrator."
