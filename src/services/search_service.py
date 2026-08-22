"""
Office search service used by the legacy Messenger/WhatsApp adapters.

The service keeps the adapter-facing string response while sourcing data
from the shared CSV office directory.
"""

import pandas as pd

DATA_FILE = "database/offices.csv"


def search_office(query: str, city: str = "Kochi") -> str:
    """Return a concise human-readable list of matching government offices."""
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return "Office database not found. Please add database/offices.csv"

    query = str(query).strip()
    city = str(city).strip()

    results = df[
        df["type"].str.contains(query, case=False, na=False, regex=False)
        & df["city"].str.contains(city, case=False, na=False, regex=False)
    ]

    if results.empty:
        return f"No {query} found in {city}. You can add it to database/offices.csv"

    output = f"Found {len(results)} {query}(s) in {city}:\n\n"
    for _, row in results.head(5).iterrows():
        output += f"ID: {row.get('id', '')}\n"
        output += f"Name: {row.get('name', '')}\n"
        output += f"Address: {row.get('address', '')}\n"
        output += f"Officer: {row.get('officer_role', '')}\n"
        output += f"Email: {row.get('email', '')}\n"
        output += "---\n"

    output += "\nReply with the ID to file a complaint."
    return output
