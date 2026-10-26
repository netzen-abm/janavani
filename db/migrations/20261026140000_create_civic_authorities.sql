-- Canonical, source-backed authority directory consumed by Web and Telegram.
-- Schema changes belong to versioned migrations, never repository construction.
CREATE TABLE IF NOT EXISTS public.civic_authorities (
    authority_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    authority_type TEXT NOT NULL,
    jurisdiction JSONB NOT NULL DEFAULT '{}'::jsonb,
    primary_contact JSONB,
    cc_contacts JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    verification_status TEXT NOT NULL,
    last_verified_at TEXT
);

CREATE INDEX IF NOT EXISTS civic_authorities_type_city_idx
    ON public.civic_authorities (authority_type);

COMMENT ON TABLE public.civic_authorities IS
    'Canonical authority directory. Populate only from traceable sources; verified destinations must have explicit evidence.';
COMMENT ON COLUMN public.civic_authorities.source_refs IS
    'Traceable source references supporting the authority record; never treat an unsourced record as verified.';
COMMENT ON COLUMN public.civic_authorities.verification_status IS
    'Verification state for the record; only explicitly VERIFIED records with a usable destination may be offered for citizen action.';
