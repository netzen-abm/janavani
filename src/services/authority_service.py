"""Canonical authority lookup service.

This adapter keeps the current CSV directory useful while returning the
canonical Authority domain object instead of leaking Pandas/DataFrame details
into callers.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.domain.authority import Authority, AuthoritySource

DATA_FILE = Path("database/offices.csv")


def find_authorities(
    department: str,
    location: str,
    *,
    data_file: Path = DATA_FILE,
) -> list[Authority]:
    """Find candidate authorities by department/type and city.

    Directory rows are treated as unverified until source provenance is
    established; this method therefore never marks a result as verified.
    """
    department = str(department).strip()
    location = str(location).strip()
    if not department:
        raise ValueError("department is required")
    if not location:
        raise ValueError("location is required")

    if not data_file.exists():
        return []

    frame = pd.read_csv(data_file)
    required = {"type", "city"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"office directory missing columns: {sorted(missing)}")

    matches = frame[
        frame["type"].astype("string").str.contains(department, case=False, na=False, regex=False)
        & frame["city"].astype("string").str.contains(location, case=False, na=False, regex=False)
    ]

    authorities: list[Authority] = []
    for row in matches.to_dict(orient="records"):
        name = str(row.get("name") or row.get("office") or row.get("type") or "").strip()
        if not name:
            continue
        authorities.append(
            Authority.create(
                name,
                "government_office",
                jurisdiction={"city": str(row.get("city") or "").strip()},
                postal_addresses=[str(row["address"]).strip()] if row.get("address") else [],
                contact_points=[str(row["phone"]).strip()] if row.get("phone") else [],
                official_urls=[str(row["website"]).strip()] if row.get("website") else [],
                source_refs=[
                    AuthoritySource(
                        source_id="office-directory-csv",
                        source_type="OTHER",
                        uri=str(data_file),
                    )
                ],
            )
        )

    return authorities


__all__ = ["DATA_FILE", "find_authorities"]
