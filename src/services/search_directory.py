# src/services/search_directory.py
# Provider for the shared Authority Discovery capability.

import pandas as pd


def search_office_records(query: str, location: str | None = None) -> list[dict]:
    """Return structured authority records without channel-specific formatting."""
    try:
        df = pd.read_csv("database/offices.csv")
    except FileNotFoundError:
        return []

    results = df[
        df["type"].astype(str).str.contains(query, case=False, na=False)
    ]

    if location:
        results = results[
            results["city"].astype(str).str.contains(location, case=False, na=False)
        ]

    return results.head(5).to_dict(orient="records")


def search_office(query: str, city: str = "Kochi") -> str:
    """Backward-compatible presentation helper for existing callers."""
    records = search_office_records(query=query, location=city)
    if not records:
        return f"No {query} found in {city}. You can add it to database/offices.csv"

    output = f"Found {len(records)} {query}(s) in {city}:\n\n"
    for row in records:
        output += f"ID: {row.get('id', '')}\n"
        output += f"Name: {row.get('name', '')}\n"
        output += f"Address: {row.get('address', '')}\n"
        output += f"Officer: {row.get('officer_role', '')}\n"
        output += f"Email: {row.get('email', '')}\n"
        output += "---\n"

    output += "\nReply with the ID to file a complaint."
    return output
