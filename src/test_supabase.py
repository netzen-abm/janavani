import os
from supabase import create_client
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("Connecting to Supabase...")

supabase = create_client(url, key)

# Test query
response = supabase.table("offices").select("*").limit(1).execute()

print("=================================")
print("✅ Connection Successful")
print("=================================")
print(response.data)
