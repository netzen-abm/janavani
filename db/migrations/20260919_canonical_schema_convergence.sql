-- Janavani — PostgreSQL schema convergence audit/upgrade
-- STATUS: READY FOR CONTROLLED DEV/STAGING EXECUTION / NOT PRODUCTION ACTIVATION
-- Purpose: converge the currently observed legacy-compatible database shape
-- with the canonical Janavani durable persistence contract.
--
-- This migration is intentionally additive/rename-first and preserves values.
-- It MUST be tested on a disposable restore before any shared environment.

BEGIN;

-- 1. Canonical Case column names.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_cases'
          AND column_name='jurisdiction'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_cases'
          AND column_name='jurisdiction_json'
    ) THEN
        ALTER TABLE public.civic_cases RENAME COLUMN jurisdiction TO jurisdiction_json;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_cases'
          AND column_name='claims'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_cases'
          AND column_name='subject_claims_json'
    ) THEN
        ALTER TABLE public.civic_cases RENAME COLUMN claims TO subject_claims_json;
    END IF;
END $$;

-- 2. Canonical Case consent references are represented by the normalized
-- consent table. Preserve any legacy JSON reference column until an explicit
-- data migration removes it.
ALTER TABLE public.civic_cases
    ADD COLUMN IF NOT EXISTS consent_refs jsonb NOT NULL DEFAULT '[]'::jsonb;

-- 3. Canonical submission names.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_case_submissions'
          AND column_name='transport'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_case_submissions'
          AND column_name='channel'
    ) THEN
        ALTER TABLE public.civic_case_submissions RENAME COLUMN transport TO channel;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_case_submissions'
          AND column_name='status'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='civic_case_submissions'
          AND column_name='state'
    ) THEN
        ALTER TABLE public.civic_case_submissions RENAME COLUMN status TO state;
    END IF;
END $$;

-- 4. Canonical submission delivery fields.
ALTER TABLE public.civic_case_submissions
    ADD COLUMN IF NOT EXISTS document_ref text,
    ADD COLUMN IF NOT EXISTS ack_ref text,
    ADD COLUMN IF NOT EXISTS error_code text,
    ADD COLUMN IF NOT EXISTS retry_count integer NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS idempotency_key text;

-- 5. Preserve existing destination data while converging the type.
-- The current inspected environment has zero rows in this table. On a
-- populated environment this must be reviewed against the authority contract
-- before type conversion.
DO $$
DECLARE
    current_type text;
BEGIN
    SELECT data_type INTO current_type
    FROM information_schema.columns
    WHERE table_schema='public'
      AND table_name='civic_case_submissions'
      AND column_name='destination_ref';

    IF current_type = 'jsonb' THEN
        ALTER TABLE public.civic_case_submissions
            ALTER COLUMN destination_ref TYPE text USING destination_ref::text;
    END IF;
END $$;

-- 6. Canonical idempotency invariant.
UPDATE public.civic_case_submissions
SET idempotency_key = submission_id
WHERE idempotency_key IS NULL;

ALTER TABLE public.civic_case_submissions
    ALTER COLUMN idempotency_key SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS civic_case_submissions_idempotency_key_uidx
    ON public.civic_case_submissions(idempotency_key);

-- 7. Canonical event metadata is optional but supported by the contract.
ALTER TABLE public.civic_case_events
    ADD COLUMN IF NOT EXISTS metadata_json jsonb;

COMMIT;
