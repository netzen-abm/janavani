# src/tools/search_directory.py
# Finds govt offices from CSV

import pandas as pd

def search_office(query: str, city: str = "Kochi") -> str:
    """
    Input: query="ration shop", city="Kochi"
    Output: List of offices
    """
    try:
        df = pd.read_csv("database/offices.csv")
    except FileNotFoundError:
        return "Office database not found. Please add database/offices.csv"

    # Search by type and city
    results = df[
        df['type'].str.contains(query, case=False, na=False) & 
        df['city'].str.contains(city, case=False, na=False)
    ]

    if results.empty:
        return f"No {query} found in {city}. You can add it to database/offices.csv"

    output = f"Found {len(results)} {query}(s) in {city}:\n\n"
    for index, row in results.head(5).iterrows():
        output += f"ID: {row['id']}\n"
        output += f"Name: {row['name']}\n"
        output += f"Address: {row['address']}\n"
        output += f"Officer: {row['officer_role']}\n"
        output += f"Email: {row['email']}\n"
        output += "---\n"
    
    output += "\nReply with the ID to file a complaint."
    return output
