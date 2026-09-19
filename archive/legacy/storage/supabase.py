from supabase import create_client

from core.config import Config


supabase = None

if Config.SUPABASE_URL and Config.SUPABASE_ANON_KEY:

    supabase = create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_ANON_KEY
    )
