-- Janavani privacy boundary: remove citizen narrative content from durable Case storage.
-- This migration is intentionally separate from the canonical schema migration.
-- Execute only after backup/restore evidence and a privacy-impact review.
--
-- After this migration, civic_cases retains lifecycle metadata and an opaque
-- case identifier; citizen narrative content is not retained by Janavani.

BEGIN;

ALTER TABLE public.civic_cases
    DROP CONSTRAINT IF EXISTS civic_cases_narrative_nonempty;

UPDATE public.civic_cases
SET subject = case_type,
    narrative = '',
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- Operational follow-up:
-- 1. Verify no application/API path depends on durable narrative retrieval.
-- 2. Scrub/delete existing citizen document/evidence blobs according to the
--    separately approved retention/deletion procedure.
-- 3. Verify logs, telemetry and backups do not retain raw citizen content.
-- 4. Do not treat this migration as permission to collect new citizen content.
