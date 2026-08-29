import pandas as pd

DATA_FILE = "database/offices.csv"


def find_offices(district: str, department: str = None, limit: int = 5):
    try:
        # --------------------------------------
        # 📂 LOAD DATA
        # --------------------------------------
        df = pd.read_csv(DATA_FILE)

        # --------------------------------------
        # 🧹 NORMALIZE COLUMNS
        # --------------------------------------
        df.columns = df.columns.str.strip().str.lower()

        # Ensure required columns exist
        if "district" not in df.columns:
            return []

        if "type" not in df.columns:
            df["type"] = ""

        if "name" not in df.columns:
            df["name"] = "Unknown Office"

        if "city" not in df.columns:
            df["city"] = ""

        # --------------------------------------
        # 🧹 CLEAN DATA
        # --------------------------------------
        df["district"] = df["district"].astype(str).str.strip().str.lower()
        df["type"] = df["type"].astype(str).str.strip().str.lower()
        df["name"] = df["name"].astype(str).str.strip()
        df["city"] = df["city"].astype(str).str.strip()

        district = str(district).strip().lower()
        department = str(department).strip().lower() if department else ""

        # --------------------------------------
        # 🔍 FILTER BY DISTRICT (PARTIAL MATCH)
        # --------------------------------------
        results = df[df["district"].str.contains(district, na=False)]

        if results.empty:
            return []

        # --------------------------------------
        # 🧠 SCORING (AI-LIKE MATCHING)
        # --------------------------------------
        def score_row(row):
            score = 0

            # Base district match
            score += 5

            # Department relevance
            if department and department in row["type"]:
                score += 5

            # Keyword hints (extensible)
            keywords = ["hospital", "ration", "panchayat", "police"]
            for kw in keywords:
                if kw in row["type"]:
                    score += 1

            return score

        results = results.copy()  # avoid pandas warning
        results["score"] = results.apply(score_row, axis=1)

        # --------------------------------------
        # 📊 SORT + LIMIT
        # --------------------------------------
        results = results.sort_values(by="score", ascending=False).head(limit)

        # --------------------------------------
        # 📤 RETURN CLEAN DATA
        # --------------------------------------
        return results.drop(columns=["score"]).to_dict(orient="records")

    except FileNotFoundError:
        print("❌ offices.csv not found")
        return []

    except Exception as e:
        print("❌ Office search error:", e)
        return []