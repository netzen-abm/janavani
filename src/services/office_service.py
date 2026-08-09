import pandas as pd

DATA_FILE = "database/offices.csv"


def find_offices(department: str, location: str):

    try:
        # --------------------------------------
        # 📂 LOAD DATA
        # --------------------------------------
        df = pd.read_csv(DATA_FILE)

        # --------------------------------------
        # 🧹 CLEAN INPUT
        # --------------------------------------
        department = str(department).strip()
        location = str(location).strip()

        # --------------------------------------
        # 🔍 FILTER (SAFE - NO REGEX WARNING)
        # --------------------------------------
        results = df[
            df["type"].str.contains(
                department,
                case=False,
                na=False,
                regex=False   # ✅ FIXED WARNING
            )
            &
            df["city"].str.contains(
                location,
                case=False,
                na=False,
                regex=False   # ✅ FIXED WARNING
            )
        ]

        # --------------------------------------
        # 📭 NO RESULTS
        # --------------------------------------
        if results.empty:
            return None

        # --------------------------------------
        # 📤 RETURN RESULTS
        # --------------------------------------
        return results.to_dict(orient="records")

    except FileNotFoundError:
        print("❌ offices.csv not found")
        return None

    except Exception as e:
        print("❌ Office search error:", e)
        return None