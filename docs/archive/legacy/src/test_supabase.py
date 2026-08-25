# Archived diagnostic integration script preserved during storage cleanup.
# Source: src/test_supabase.py
#
# This script intentionally remains outside the active test suite because it
# requires live Supabase credentials and performs a real network/database call.

import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url:
    raise RuntimeError("SUPABASE_URL is missing")
if not key:
    raise RuntimeError("SUPABASE_ANON_KEY is missing")

supabase = create_client(url, key)
response = supabase.table("offices").select("*").limit(1).execute()
print(response.data)
