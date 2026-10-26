-- Remove non-operational table privileges from API-facing Supabase roles.
-- These tables contain encrypted Telegram updates and provider-to-principal identity links.
-- Runtime access remains limited to the dedicated NOLOGIN roles granted by the runtime-role
-- migrations; service_role keeps its ordinary data DML permissions but cannot TRUNCATE,
-- create triggers on, or add foreign-key references to these tables.
REVOKE TRUNCATE, REFERENCES, TRIGGER
    ON TABLE public.telegram_update_inbox
    FROM PUBLIC, anon, authenticated, service_role;

REVOKE TRUNCATE, REFERENCES, TRIGGER
    ON TABLE public.external_identity_links
    FROM PUBLIC, anon, authenticated, service_role;
