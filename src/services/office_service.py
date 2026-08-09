import pandas as pd

DATA_FILE = "database/offices.csv"

def find_offices(department: str, district: str):

    try:
        df = pd.read_csv(DATA_FILE)

        results = df[
            (df["type"].str.contains(department, case=False, na=False)) 
            (df["district"].str.contains(district, case=False, na=False)) &
            (df["city"].str.contains(district, case=False, na=False))
        ]

        if results.empty:
            return []

        return results.to_dict(orient="records")

    except Exception as e:
        print("❌ Office search error:", e)
        return []