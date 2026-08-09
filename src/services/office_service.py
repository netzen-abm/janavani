import pandas as pd

DATA_FILE = "database/offices.csv"

def find_offices(department: str, location: str):

    try:
        df = pd.read_csv(DATA_FILE)

        # We only have city for now
        results = df[
            (df["type"].str.contains(department, case=False, na=False)) &
            (df["city"].str.contains(location, case=False, na=False))
        ]

        if results.empty:
            return None   # 👈 IMPORTANT CHANGE

        return results.to_dict(orient="records")

    except Exception as e:
        print("❌ Office search error:", e)
        return None