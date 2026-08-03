import os
from supabase import create_client

# Read environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

print("====================================")
print(" Janavani Supabase Connection Test ")
print("====================================")

# Check environment variables
if not SUPABASE_URL:
    raise Exception("❌ SUPABASE_URL environment variable not found.")

if not SUPABASE_KEY:
    raise Exception("❌ SUPABASE_ANON_KEY environment variable not found.")

print("✅ Environment variables loaded")

try:
    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Simple query to verify connection
    response = supabase.table("pg_tables").select("*").limit(1).execute()

    print("✅ Successfully connected to Supabase!")

except Exception as e:
    print("❌ Connection failed")
    print(e)
