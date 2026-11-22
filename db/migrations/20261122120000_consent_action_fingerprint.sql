-- Stable idempotency key for one explicit citizen consent action.
-- The action identifier itself is never persisted; only its SHA-256 fingerprint is stored.
BEGIN;

ALTER TABLE public.civic_case_consents
    ADD COLUMN IF NOT EXISTS action_fingerprint text;

CREATE UNIQUE INDEX IF NOT EXISTS civic_case_consents_subject_action_uidx
    ON public.civic_case_consents (subject_id, action_fingerprint)
    WHERE action_fingerprint IS NOT NULL;

COMMIT;
