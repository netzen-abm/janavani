import os
from dotenv import load_dotenv
from supabase import create_client

# Load local .env (works locally, harmless on Render)
load_dotenv()

# Read environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

print("=" * 50)
print("SUPABASE_URL:", url)
print("SUPABASE_ANON_KEY exists:", bool(key))
print("=" * 50)

if not url:
    raise Exception("SUPABASE_URL is missing")

if not key:
    raise Exception("SUPABASE_ANON_KEY is missing")

print("Connecting to Supabase...")

supabase = create_client(url, key)

print("✅ Connected!")

response = supabase.table("offices").select("*").limit(1).execute()

print("====================================")
print("✅ Supabase Connection Successful")
print("====================================")
print(response.data)
